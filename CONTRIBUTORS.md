# How to Contribute

This is a very young project, and the codebase is moving quickly -- but there are plenty of ways to help. This document 
provides some guidelines for when you're ready to ask questions, file issues, submit code, or submit examples of working Ansible 
Container projects. 

For additional information about contributing to the project, or to review our *Code of Conduct* and our *Contributor's License
Agreement*, please visit [Community Information and Contributing](<https://docs.ansible.com/ansible-container/community/index.html).


## Ask questions and file issues

Please use the GitHub issue tracker for all issues with, and questions about, the project. We will respond to issues as quickly as possible.

When filing an issue, observing the following guidelines will lead to a quicker response:

- Search existing issues to see if someone else has asked the same question or raised a similar issue.
- State the question or nature of the issue clearly in the title.
- When reporting a bug, please complete the issue template with as much detail as possible. The template asks for information about your environment,
  the command you executed, stracktraces, etc. Answer each question thoroughly, and include code snippets, screen shots, or anything you feel will 
  help a developer reproduce and troubleshoot the issue.

## Contribute code

Code submissions are accepted via pull requests, and they are always welcome! We may not accept them all, but we are always happy to review and 
discuss them with you.

Before submitting a large pull request for a new feature, we suggest joining the [Ansible Container Mailing List](https://groups.google.com/forum/#!forum/ansible-container),
and submitting a topic to discuss the feature prior to submission.

We reserve the right to reject submissions that are not a good fit for the project or not in keeping with the intended direction of the project. If you are unsure 
as to whether a feature is a good fit, take the time to start a discussion on the mailing list.

Please observe the following when submitting a PR:

- Follow the [gitflow](https://github.com/nvie/gitflow) branching model.
- Submit requests to the *develop* branch.
- Include unit and integration tests for new features.
- Document new features in [docs/rst](./docs/rst).
- Limit the scope of a submission to a single feature or bug fix.
- Ensure tests are passing.

### Running tests

Unit and integration tests are found in the [test subdirectory](./test). When a pull request is submitted, tests are automatically executed on
Travis to test the submitted code.

Running tests locally requires cloning the Ansible Container repo, and setting up your environment to run from source. See the [Installation 
Guide](https://docs.ansible.com/ansible-container/installation.html) for assistance. 

Test execution is initiated by running the [test/run.sh](./test/run.sh) script found in your local copy of Ansible Container. For example:

```
$ cd ansible-container
$ ./test/run.sh 
```

If the *local-test* image does not exist, the script will create it by running `ansible-container build` within the [test/local project](./test/local). 
Once the image is available, tests are executed within a container via `ansible-container run`. Subsequent runs of the script will use the existing 
*local-test* image and skip the build step. 

Test execution occurs exactly the same way on Travis as it does in a local development environment. So if tests run successfully in your local 
environment, they *should* run successfully on Travis.

## Provide examples

Examples of working Ansible Container playbooks are very useful! Please feel free to provide pull requests linking
to examples from your own repos in [EXAMPLES.md](./EXAMPLES.md), or submit them to [ansible-container-examples](https://github.com/ansible/ansible-container-examples).

<p>&nbsp;</p>
<p>Thanks for trying out Ansible Container!</p>

