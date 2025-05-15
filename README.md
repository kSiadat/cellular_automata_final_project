## Background
This project is my final year project from studying BSc Computer Science at the University of Birmingham.  
I finished this project in September 2023.  
During the course of my work I recieved guidance from my supervisor Jens Christian Claussen.  
While studying in my 3rd year I completed a module called Evolutionary Computation, taught by Jens. As part of that module I learnt about cellular automata and found it very interesting, so I decided that for my final year project I would do a research project on CAs. In particular I decided to look for rules in a 2D CA that would produce Sierpinski patterns, or at least produce patterns that follow the same type of population sequence.  
The project was successful, and I found 2D rules that produce Sierpinski patterns in place every 2^n timesteps. The patterns are similar to ruke 90 in the 1D CA but don't require any kind layering.  
There are also patterns that would produce a kind of Sierpinski pyramid if you were to layer them.  
All of the findings and necessary background information for the topic is explained in more detail in the report, named 'siadat-2155638.pdf'.  
## Structure
The folders contain images from each timestep of the simulation of a specific rule, the number of which is at the end of the name. This is not necessary to look through but I left it in because I think it's interesting.  
The python files are used for the simulation, as well as for storing the results in the database, and filtering through those results.  
The databases store the population sequences of a random sample of rules.  
And the file 'siadat-2155638.pdf' is the main report which properly explains the project in detail. As well as explaining the theory behind the project it also has at the end, a brief explanation of the code.  
## More info
If you find this interesting but want a more visual way of looking at the patterns, you can go to the 'patterns' repository and have a look in the 'user_ca' folder. There you will find a program that allows you to run the simulation for any rule you like and see the results displayed in real time.  
