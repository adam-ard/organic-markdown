Here is a list of things that I need to make sure to test.

- Go back to handle_cmd and make sure that everything is returning a number, so that sys.exit will get called with an exit code
- get rid of append functionality
   - it makes testing harder
   - makes the text order non-determinate
   - doesn't give you much for the little you get.
   - maybe hold onto it? because of documentation? But treat using it like an anti-pattern, and if over time I never need it, then get rid of it?
- Add some sort or way to make refs end with a new line (example @<name+@>, or even @<name+++@> for 3 newlines)
- Add namespaces per file for refs (ex. funcs::get_name)
   - or maybe we only add namespaces for files if there is a namespace property in the header yaml?
- make the test common stuff have a function that takes cmd and expected
- run things through a python linter, to make it always consistent



Thoughts:
  -- unit tests should go with the individual files.
  -- output source is throw-away, like compiled code.
  -- integration tests are handled well by torture test. Will this always be the case?
