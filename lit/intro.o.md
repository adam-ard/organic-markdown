# Organic Markdown Source

In the spirit of eating your own dog food, what follows is the `omd` source code written in **literate form**.

You might be wondering: *How is this possible?*
*How can you write a literate programming tool using the literate style of the tool itself?*
Isn't that a chicken-and-egg problem?

Let me explain.

I originally wrote `omd` as a single, monolithic Python script—not in any literate style. After experimenting and tweaking it for a while, it became stable enough that I decided to take a more disciplined approach: documenting and testing it properly.

And what better way to do that than with **literate programming**?

So I used that simple, brute-force bootstrapping script, my original `omd`,  to reimplement `omd` in the literate style I had envisioned. Eventually, when the source code generated from these literate files was as stable and complete as the original bootstrap script, I started using it to generate the `omd` script itself.

**OMD is now implemented in OMD.**

👉 [View the Code Layout](code.o.md)
