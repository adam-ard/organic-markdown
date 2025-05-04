# Organic Markdown Source

In the spirit of eating your own dog food, below is the `omd.py`
source code in literate form. How is this done? You ask. How can you
write a literate programming tool in the literate style of the tool
itself? Isn't there a chicken and egg problem here? Let me explain.

I first wrote `omd.py`, all in one big file, not in any literate
style. After playing with it and tweaking it, it finally became stable
enough that I decided to try to do a more disciplined job of
documenting and testing it. What better way to do that then with
literate programming?! So I have been using that little, brute-force,
bootstrapping python script to re-impliment OMD in an OMD
style. Eventually, when the source I emit from these literate files is
as stable as the first bootstrap script, I'll remove the bootstrap
script (`omd.py`) from the repo. Then OMD will be implimented in OMD.

As I go through this process, all I really need to do at first is diff
the output of these OMD files with the `omd.py` bootstrapping
script. If they are the same, then I am golden. This will get me
pretty far. Eventually though, I will want to start emitting python
that isn't identical to the bootstrapping script. By that time, I hope to
have enough good documentation and testing in place, that I can
confirm its validity that way. Fingers-crossed.
