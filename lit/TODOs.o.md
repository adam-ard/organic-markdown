Here is a list of things that I need to make sure to test.

- Test that blocks with no names (this happens a lot for tangle blocks) don't all append the content to each other
- Go back to handle_cmd and make sure that everything is returning a number, so that sys.exit will get called with an exit code
