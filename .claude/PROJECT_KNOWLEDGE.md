This is a new repo for a terraform module. One of many produced by InfraHouse https://github.com/infrahouse

Many other Terraform modules need a lambda. https://github.com/infrahouse/terraform-aws-actions-runner/tree/main/modules/record_metric is a prominent
example.
By creating this module, I plan to reduce duplication across InfraHouse repositories.
Another reason for a separate lambda module is ISO27001 requirements. A lambda error rate needs to be monitored.
And not only send a notification when the lambda exited with the error. Different lambdas have different requirements.
Some lambdas need to notify a user by email as soon as an error happens. Some lambda tolerate some errors and need to send an alert email only if the error
rate is too high.
Obvoiusly, I need a lambda to work with multiple Python version (only Python btw) and on arm64 and amd64.
I will need Terraform tests that cover AWS provider version 5 and 6.
