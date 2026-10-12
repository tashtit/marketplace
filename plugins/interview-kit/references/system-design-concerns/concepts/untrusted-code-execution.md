# Executing Untrusted Code

When a system runs code that users submit, where that code runs and what it is allowed to do become
the central design decision. Get it wrong and one submission can compromise or crash the service
[S6].

## When it applies

- Users submit code, and the system must run it and report what happened [S6].
- The work is CPU-intensive and may misbehave, for example an infinite loop or a memory leak [S6].

## Why it matters

The source states three distinct risks of running submitted code in the same place as the service
[S6]:

- **Security.** Malicious code could take the server down, delete data, send data to a third party,
  or use the machine for other abuse such as mining or launching attacks [S6].
- **Performance.** Running code is CPU-intensive and can crash an unmanaged server [S6].
- **Isolation.** If the code runs in the API server's process and crashes, the server goes down with
  it and no other requests are processed [S6].

The source treats running submissions directly on the API server as the bad answer for these
reasons. It calls it a terrible idea [S6].

## Approaches and tradeoffs

**In the API server.** The simplest option: save the code to a local file, run it and capture the
output. It carries all three risks above [S6].

**In a virtual machine.** An isolated environment that can be reset if something goes wrong, so a
crash in the VM does not affect the host or other users [S6]. A VM includes a full operating system,
which adds overhead but gives strong isolation [S6]. Challenges [S6]:

- VMs are resource-intensive and slow to start, so capacity has to be managed carefully.
- Their lifecycle has to be managed so you neither run out of resources nor leave idle VMs running,
  which is costly.

**In a container.** The source calls this great and arguably optimal [S6]. Containers share the host
kernel and package only the application and its dependencies. They are therefore lighter and start
faster than VMs, at the price of weaker isolation [S6]. There is one container image per supported
runtime, and containers are reused across submissions instead of being created for each one, which
reduces resource use [S6]. Challenges [S6]:

- Because the kernel is shared, containers must be configured and secured so that a user cannot
  break out to the host.
- Resource limits must stop any one submission from starving the others.

**In a serverless function.** Also called great, with one function per runtime triggered for each
submission [S6]. Such functions scale up and down automatically, which suits work that is CPU-intensive
or unpredictable in volume [S6]. Challenges: cold starts add latency to the first request, and
resource limits can hurt long-running or resource-heavy code [S6].

## How to decide

The source's choice between the two "great" options comes down to two stated conditions: it expects
little variance in submission volume, and it wants to avoid cold-start latency. On that basis it
picks containers over serverless functions [S6]. Read in reverse, unpredictable volume is the case
the source gives for serverless [S6].

## Hardening the sandbox

Running code in a container is a big step on its own. The source then adds these measures [S6]:

- **Read-only filesystem.** Mount the code directory read-only. Write output to a temporary
  directory that is deleted shortly after the run completes [S6].
- **CPU and memory bounds.** A container that exceeds its limits is killed, which prevents resource
  exhaustion [S6].
- **An explicit timeout.** Kill the process after a set limit; the source's example is 5 seconds.
  This stops infinite loops, and the source ties the limit to its 5-second latency requirement
  [S6].
- **No network access.** Disable networking so that user code cannot make external calls. The source
  names VPC security groups and NACLs as one way to block all traffic except essential connections
  [S6].
- **Restricted system calls.** Use seccomp to limit the system calls the container can make, so that
  user code cannot compromise the host [S6].

The sandbox itself makes no outbound calls. The worker that manages it invokes it synchronously,
waits for it to finish, and reads the result from stdout or a mounted volume [S6]. *(Example: via
Docker's exec API [S6].)*

## Depth expected when explaining it

According to the source, an interview does not require implementation detail for each measure. A
single sentence that names containers, limited network access, CPU and memory bounds and a timeout
is likely enough unless the interviewer asks for more [S6].

## Failure modes

- **A submission compromising the host or exfiltrating data**, when code runs on the service itself
  [S6].
- **One submission's crash taking down the service**, when it shares the service's process [S6].
- **Escape from a shared-kernel sandbox**, when containers are not hardened [S6].
- **One submission starving the others**, when there are no resource limits [S6].
- **Infinite loops holding a worker indefinitely**, when there is no timeout [S6].
- **Idle VMs accumulating cost**, when their lifecycle is not managed [S6].
- **Cold-start latency on the first request**, with serverless execution [S6].

## Not covered by sources

- How containers are pooled and reset between submissions, given that they are reused.
- What happens to state left behind by one submission before the next one uses the same container.
- Which system calls should be allowed, and how that list is maintained per runtime.
- How to choose time and memory limits per problem, as opposed to one global limit.
- How to detect and respond to an attempted sandbox escape.
- When stronger isolation than a container is worth its cost.

## Sources

- **[S6]** Hello Interview — Design a Coding Platform Like LeetCode —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/leetcode>
