* Use RST docstrings in Python
* Pin Python dependencies to a major version. Use ~= syntax. I.e. `requests ~= 2.31` instead of `requests>=2.31.0,<3.0.0`
* Use Makefile-example as a Makefile example.
* When a variable or output description is too long, use HEREDOC construction to wrap lines.
* The module should only require providers it actually uses to create direct resources. Child modules should take care 
  of their required providers.

## InfraHouse Terraform testing
* The root module must define variables in terraform.tfvars
