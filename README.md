Copyright(c) 2013 Yibin Lin (yibinl@cs.cmu.edu)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Dependency: Python 2.7, Networkx 1.7+, GNU make, Numpy

Usage: For a demo, simply issue command:

    make

to see a small demo of simulating a influence network using base network as Enron Email dataset. The output will be stored in the file "enron_influence_graph.csv".

The Enron dataset in this demo is from UC Berkeley Enron Email Analysis, a database representation of Enron dataset built by Andrew Flore and Jeff Heer (http://bailando.sims.berkeley.edu/enron_email.html). The original Enron dataset was released by MIT, SRI and CMU. 

Specifically, the graph file format is as follows:

1. Each edge occupies one line
2. In each line: {from_edge},{to_edge},{weight}

In Enron case the weight is the number of email messages. The output graph format is the same.

