# AgentCore Deployment Troubleshooting

## Symptom

Running the Quest agents on Amazon Bedrock AgentCore sometimes fails with the message **“Runtime initialization time exceeded. Please make sure that initialization completes in 60s.”**. This is the same failure mode described as an invocation timeout in the [Troubleshoot AgentCore Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-troubleshooting.html#troubleshoot-runtime-timeout) guide—AgentCore tears down the session when a runtime container cannot finish its startup handshake fast enough or respond to `/invocations` in time.

### Canonical references

- [Troubleshoot AgentCore Runtime – 504 Gateway Timeout](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-troubleshooting.html#troubleshoot-runtime-timeout): explains that timeouts usually come from container startup issues (port 8080 not exposed, `/invocations` missing, not ARM64, retry logic problems).
- [Troubleshoot AgentCore Runtime – RuntimeClientError and log locations](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-troubleshooting.html#runtime-client-error): points to the CloudWatch log group pattern `/aws/bedrock-agentcore/runtimes/<agent_id>-<endpoint_name>/runtime-logs`.
- [Troubleshoot AgentCore Runtime – Debugging container issues](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-troubleshooting.html#debugging-container-issues): recommends pulling the same image and running it locally to spot startup failures.
- [Troubleshoot AgentCore Runtime – Long-running tool guidance](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-troubleshooting.html#troubleshoot-runtime-long-running): shows how to emit `context.ping(status="HEALTHY_BUSY")` during long initialization so the session stays alive.
- [AgentCore Runtime service contract](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-service-contract.html) and [HTTP protocol contract](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-http-protocol-contract.html): define the requirement to expose port `8080`, implement `/invocations`, and respond to `/ping`.

## Investigation workflow

1. **Look at runtime logs first**  
   Use the CloudWatch group from the RuntimeClientError section above to find container startup errors:  
   ```bash
   aws logs tail /aws/bedrock-agentcore/runtimes/<agent_id>-<endpoint_name>/runtime-logs --follow
   ```  
   Missing imports, segmentation faults, or dependency installs happening at boot are common culprits.

2. **Verify the runtime image meets the contract**  
   Double-check that the deployed artifact exposes `8080`, implements `/invocations`, and builds for `arm64` per the service contract. If you are zipping code instead of a container, confirm that the generated bundle contains only the files that AgentCore should run (no stray `.venv` folders or build artifacts). The `.gitea/workflows/deploy.yaml` workflow already excludes `.*venv*`, `build/`, `docs/`, etc.; make similar exclusions locally when running `deploy_cipher_agents.sh`.

3. **Run the agent locally with the same payload**  
   Follow the “Debugging container issues” steps: pull the built image (or run `agentcore local`) and send a `curl` request to `http://localhost:8080/invocations`. Reproducing the issue outside Bedrock is the fastest way to see blocking calls or misconfigured paths before the 60‑second limit hits.

4. **Emit heartbeat pings while doing heavy initialization**  
   The AgentCore docs recommend calling `context.ping(status="HEALTHY_BUSY")` on a background task every ~30 seconds (see the “Long-running tool” advice). To do that, include the `context` parameter in your `@app.entrypoint` signature and start an async ping loop while large models, Swarm graphs, or embeddings load.

5. **Keep lifecycle settings tidy**  
   If you customized lifecycles, ensure `idleRuntimeSessionTimeout` is at least 60 seconds (per [runtime lifecycle settings](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-lifecycle-settings.html)). A too-aggressive idle timeout makes it look like initialization failed even when the container eventually comes online.

## Cipher Quest–specific mitigation steps

- **Move heavy startup work out of the import path**  
  `cipher_command_agent.py` builds the entire Strands multi-agent swarm as soon as the module is imported (`cipher_command_agent.py:24-145`). Any network calls (for example, `boto3.Session()` resolving the region or `BedrockModel` contacting Bedrock) all happen before AgentCore can reach your entrypoint. Wrap that setup code in a lazy factory or guard it with a module-level flag so initialization finishes quickly on cold start.

- **Accept `context` and send heartbeats**  
  Update `strands_agent_bedrock` to accept a second `context` argument and start a ping loop modeled after the [official snippet](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-troubleshooting.html#troubleshoot-runtime-long-running). Even if agent orchestration takes minutes, the runtime stays alive as long as you report `HEALTHY_BUSY`.

- **Preload dependencies inside the deployment package**  
  The deployment script (`deploy_cipher_agents.sh`) already installs requirements before running `agentcore launch`. Make sure the packaged artifact includes the `.venv` site-packages or that you build a container image with those dependencies baked in. Installing `strands`, `boto3`, or scientific libraries at startup will exceed the 60‑second threshold.

- **Trim unused imports and optional tooling**  
  If portions of the swarm (for example, steganography helpers) are not required for the current GameDay, guard their imports or load them lazily. Every unused dependency removed from `requirements.txt` directly reduces initialization time.

- **Test payload handling locally**  
  Use the `agentcore invoke` samples in `deploy_cipher_agents.sh` after each change so you can catch malformed payloads that would otherwise manifest as timeouts or 422 errors in production.

## Redeploy checklist

1. `source .venv/bin/activate` and reinstall requirements after any dependency changes.
2. `agentcore configure --entrypoint cipher_command_agent.py --execution-role <role-arn> --name cipher_quest_agent` (only needed once per new role/agent).
3. `agentcore launch --verbose` to push the updated artifact; watch the CLI output for upload size and digest.
4. `agentcore describe` to grab the runtime ID for the CloudWatch log group mentioned earlier.
5. `aws logs tail /aws/bedrock-agentcore/runtimes/<agent_id>-<endpoint>/runtime-logs --follow` while invoking `agentcore invoke '{"prompt":"Decrypt ..."}'` to ensure cold starts complete well under 60 seconds.

Following the official troubleshooting flow plus the Cipher Quest–specific adjustments above should keep the runtime responsive enough for Bedrock AgentCore’s initialization window.
