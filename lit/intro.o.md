# Organic Markdown Source

In the spirit of eating your own dog food, following is the `omd` source code in literate form. How is this done? You ask. How can you write a literate programming tool in the literate style of the tool itself? Isn't there a chicken and egg problem here? Let me explain.

I first wrote `omd`, all in one big file, not in any literate style. After playing with it and tweaking it, it finally became stable enough that I decided to try to do a more disciplined job of documenting and testing it. What better way to do that then with literate programming?! So I used that little, brute-force, bootstrapping python script to re-implement OMD in an OMD style. Eventually, when the source I emitted from those literate files was as stable as the first bootstrap script, I  started generating the omd script from them. OMD is now implemented in OMD!

[The Code Layout](code.o.md)
