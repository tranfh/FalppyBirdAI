# FlappyBirdAI

## Flappy Bird Game using AI!
![flappybird](https://i.ytimg.com/vi/WSW-5m8lRMs/maxresdefault.jpg)


This app is built using PyGame and NEAT (NeuroEvolution of Augmenting Topologies)

The game will run multiple instances of the bird and will train itself to jump through those pipes everytime


## Here is how NEAT works:
The key innovation of NEAT is the introduction of three main evolutionary operators to evolve the neural networks effectively:

Mutation: NEAT applies various mutations to the genomes, including adding or removing neurons, adding or removing connections between neurons, and adjusting the weights of connections.

Crossover: NEAT performs crossover (also known as mating) between two genomes to create offspring. This process involves combining the structure and weights of the parent genomes.

Speciation: To encourage the maintenance of diversity in the population, NEAT employs a technique called speciation. It groups genomes into species based on their similarity and then applies separate fitness evaluations for each species. This helps to protect innovation and prevents premature convergence.

Throughout the evolutionary process, the genomes that perform better on a given task (as measured by a fitness function) are more likely to reproduce and pass their genetic material to the next generation. Over time, the population evolves, and the neural networks become more complex and better adapted to the task at hand.

NEAT has been used in various applications, including reinforcement learning, control systems, and game playing. By allowing for the evolution of both neural network weights and structures, NEAT can discover innovative and efficient architectures for solving complex problems.

## What does that even mean?? 🙃

This bird needs to fly through pipes without hitting them. The bird's brain is like a simple network that decides when to flap its wings and when to stay still.

At the beginning of the game, the bird's brain is quite simple, and it doesn't know how to avoid the pipes very well. It often crashes into them and doesn't get very far.

Now, we want to make the bird smarter so it can play the game better. We use NEAT to do this. NEAT starts with many birds with slightly different brains, all of which are simple like the first one.

These birds start playing the game, and some of them do a little better than others. The birds that manage to get further and avoid the pipes live longer and have a chance to "have babies."

When birds have babies, the babies might inherit their parents' brains but with some small changes, like adding or removing a connection in their brain.

Some babies might end up with a new connection that helps them time their flapping better or react faster. These changes make them a bit smarter than their parents.

As the game continues, generations of birds keep playing, and the smarter birds have more babies. Over time, the birds' brains get more and more complex because of these changes.

Eventually, some birds become really good at the game because their brains have evolved to be very good at avoiding the pipes. These smart birds can get far in the game without crashing.

So, thanks to NEAT, we were able to make the little bird in Flappy Bird smarter and better at playing the game by evolving its brain to become more and more skilled.




