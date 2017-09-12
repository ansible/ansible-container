Roadmap for Release 1.1.0
=========================

* Enable idempotence for faster builds by fixing the following:

  * On rebuilds, when we detect that an existing image layer does not match the expected hash, we throw it away, and rebuild from that point. This forces Ansible to re-run all tasks in the role.
  * The same for failed builds. We throw away the container, and on restart force the complete re-run of all tasks in the failed role.

* Build an Ansible Service Broker (ASB) deployment engine
* Create a 'best practices' guide for deploying
