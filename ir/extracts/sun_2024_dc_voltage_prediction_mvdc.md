# DC Voltage Prediction based on CNN with Physics Information Embedding for MVDC Distribution Systems

> Derived Markdown text extracted from the PDF for ingestion.
> The PDF under `raw/` remains the source of truth.

- source_id: `sun_2024_dc_voltage_prediction_mvdc`
- raw_pdf: `raw/sun_2024_dc_voltage_prediction_mvdc/Sun et al_2024_DC Voltage Prediction based on CNN with Physics Information Embedding for MVDC.pdf`

## Extracted Text

2024 IEEE 10th International Power Electronics and Motion Control Conference (IPEMC2024-ECCE Asia) | 979-8-3503-5133-0/24/$31.00 ©2024 IEEE | DOI: 10.1109/IPEMC-ECCEAsia60879.2024.10567577

DC Voltage Prediction based on CNN with Physics
Information Embedding for MVDC Distribution
Systems
Pingyang Sun(1) , Rongcheng Wu(2) , Hongyi Wang(3) , Zhiwei Shen(1) , Gen Li(4) ,
Muhammad Khalid(5) , Georgios Konstantinou(1)
(1) School of Electrical Engineering and Telecommunications, UNSW Sydney, Australia
(2) Data Science Institute, University of Technology Sydney, Australia
(3) Department of AAU energy, Alborg University, Denmark
(4) Department of Engineering Technology and Didactics Electric Energy, DTU, Denmark
(5) Electrical Engineering Department & Interdisciplinary Research Center for Sustainable Energy Systems,
King Fahd University of Petroleum and Minerals, Saudi Arabia
email: pingyang.sun@student.unsw.edu.au, rongcheng.wu@student.uts.edu.au, howa@et.aau.dk,
zhiwei.shen@unsw.edu.au, genli@dtu.dk, mkhalid@kfupm.edu.sa, g.konstantinou@unsw.edu.au.

Abstract—Conventional neural networks (NNs), though efficient in rapid dc voltage calculations for medium-voltage direct
current (MVDC) distribution systems with diverse converter
control schemes, face accuracy challenges with untrained system
parameter distributions and topology structures. This paper
proposes a physics-embedded convolutional NN (PECNN) to
address this issue. The PECNN is enhanced with two additional
layers, including a multi-channel combination layer and a physics
operation layer. The former channel combination layer strengthens the model feature extraction capability by converting all
input channels constituted by initial data matrix into dc voltage,
current and line conductance matrix channels. The latter physics
operation layer reformulates the combined input channels by
physical connections in MVDC systems. The new layers enhance
the prediction accuracy and allow generalization of the model.
Three MVDC distribution networks with different dc voltage
levels and network layouts are used to verify the superiority of
proposed PECNN compared to other NNs in different topologies.
Index Terms—Medium-voltage dc (MVDC) system, dc voltage
estimation, neural network (NN), convolutional NN (CNN).

I. I NTRODUCTION
Medium-voltage dc (MVDC) power systems have the potential to outperform equivalent ac counterparts in many applications, especially in distribution grids. MVDC distribution
systems offer a range of network configurations, including
radial, ring, and meshed structures, enhanced by the integration
of multiple ac/dc and dc/dc converters [1], [2]. For improved
security and planning in MVDC networks, it is vital to conduct
power flow analysis for different operation scenarios as line
disconnection and converter outage, with a key focus on
accurately deriving terminal dc voltage [3].
Many numerical methods can be employed for dc voltage
calculation in MT-MVDC networks. Methods represented by
the Newton-Raphson (NR) are effective for an MVDC distribution system that utilize various converters with diverse

control schemes [4]. However, numerical methods come with
certain disadvantages such as convergence for ill-conditioned
systems, and computational complexity for large systems [4],
[5]. With advances in computer processing capabilities, the
use of neural networks (NNs) is becoming more prevalent.
Once appropriately trained, NNs can predict results in a single
forward propagation, outpacing numerical methods [6]. An
MVDC distribution system often experiences shifts in steadystate operation points due to the presence of time-variable
loads, distributed generation (DG), and energy storage systems
(ESSs) with power sharing achieved through connected converters utilizing various control schemes [7]. This underscores
the necessity for employed NNs to possess excellent generalization capabilities and adapt to varying operational scenarios
and ensure stable system performance.
Multilayer perceptron (MLP) is the widely used artificial
neural networks (ANNs) in power flow analysis [8]. MLP
can also support power flow analysis even in the absence of
comprehensive initial system data [9]. It is also employed in
optimal power flow to enhance the efficiency of traditional
methods [10] or to directly produce optimal solutions [11]–
[13]. Although MLP is effective in fixed topology structures, they encounter challenges when the system topologies
shift [14]. Compared to conventional MLP, convolutional NN
(CNN) inherently has the capability to handle input with
variable sizes due to spatial hierarchies and local connectivity
patterns, which allow adoption of different spatial dimensions
without requiring a fixed-size input vector [15].
CNN has been extensively employed in power flow studies
under uncertain contingency scenarios [16], demonstrating
efficiencies up to 100 times [17] and 350 times [18], [19] that
of traditional numerical methods for optimal power flow solutions. In addition, the Latin-hypercube sampling method has
been incorporated into a CNN to enhance training efficiency

979-8-3503-5133-0/24/$31.00 ©2024 IEEE
Authorized licensed use limited to: Xi'an University of Technology. Downloaded
on July 10,2024 at 07:45:07 UTC from IEEE Xplore. Restrictions apply.
2700

--- page break ---

in probabilistic power flow analyses [20]. The integration
of a CNN with long short-term memory (LSTM) networks
facilitates the inclusion of weather effects in power flow
determinations [21]. Nevertheless, the traditional approach to
CNN channel construction fails to fully capture the complex
relationships between node and line parameters such as node
voltage, power and line impedance that constitute the inherent
physical connections in power systems. This lack of representation leads to diminished performance when dealing with
unseen data, as it overlooks the interactions between these
key elements that fundamentally drive the electrical network
behaviors [22].
This paper proposes a novel physics-embedded CNN
(PECNN), specifically designed for terminal dc voltage estimation in MVDC distribution systems with different converter
control schemes. In this model, the input channels are reformulated to account for the relationships between voltage, power,
current at MVDC terminals and line parameters. The voltage
and current channels mutually transform through the line
conductance channel, reflecting the actual voltage and current
interactions. Moreover, a more accurate representation of the
physical connection is captured after performing multiple
reformulation calculations. This operation enhances both the
prediction accuracy and generalization capability, as it allows
the network to comprehend the complex interaction between
voltage, current, and line conductance in an MVDCs system.
II. N UMERICAL C OMPUTATION M ETHOD
Different control schemes can be adopted in dc terminallinked converters in an MVDC distribution system, including i)
dc bus voltage control, ii) dc power or current control, and iii)
power/voltage (P/V) or current/voltage (I/V) droop control [3].
Five MVDC bus types can be defined to compute the terminal
voltage based on a NR method in an MVDC system with
n buses. They are one MVDC voltage bus (slack bus), m dc
power buses, l dc current buses, k P/V droop-controlled buses,
(n − m − l − k − 1) I/V droop-controlled buses.
Eq. (1) summarizes the PF equations for dc voltage,
dc power, dc current, P/V droop-controlled and I/V droopcontrolled buses, respectively.
⎧
(i = 1)
Vdcref m,i − Vdcm,i = 0,
⎪
⎪
⎪
⎪
(i = 2, ..., m + 1)
Pdcref m,i − Pdcm,i = 0,
⎪
⎪
⎪
⎪
⎪
(i = m + 2, ..., l + m + 1)
⎨ Idcref m,i − Idcm,i = 0,
PV
(Vdcref m,i − Vdcm,i ) = 0 ,
(Pdcref m,i − Pdcm,i ) + Kdroop,i
⎪
⎪
⎪
(i = l + m + 2, ..., k + l + m + 1)
⎪
⎪
⎪
IV
⎪
− Idcm,i ) + Kdroop,i
(Vdcref m,i − Vdcm,i ) = 0
(I
⎪
⎪
⎩ dcref m,i
(i = k + l + m + 2, ..., n)

(1)
rated
PV
, Kdroop,i
where Vdcref m is usually set as rated voltage Vdcm
IV
and Kdroop,i
are the droop constants for converters with P/V
and I/V droop, respectively:
PV
rated
rated
Kdroop,i
= (Vdcm
δdroop )−1 Pdc
,

(2)

IV
rated
rated
rated
Kdroop,i
= (Vdcm
· Vdcm
δdroop )−1 Pdc
,

(3)

and δdroop is the maximum allowable dc voltage deviation
ratio [23]. Moreover, the dc power and current injected to any
MVDC buses is expressed as:



Pdcm,i = Vdcm,i n
j=1 Gdcm,ij Vdcm,j
n
Idcm,i = j=1 Gdcm,ij Vdcm,j

(4)

where Gdcm,ij is the line conductance in an MVDC system.
The dc voltage in all MVDC terminals can be derived by
executing NR algorithm [24].
Although the conventional numerical approach can derive
the terminal voltage of MVDC distribution systems accurately,
it requires repetitive computations resulting in a significant
computational expense. Therefore, it is not well-suited for
MVDC systems with many time-variable loads, DGs and ESSs
that require rapid voltage computations.
III. P ROPOSED PECNN FOR MVDC D ISTRIBUTION
N ETWORKS
A. General Network Description
Fig. 1 shows the proposed PECNN which comprises i)
one multi-channel combination layer, ii) one physics operation layer, iii) four sets of six encoder blocks with two
convolutional layers. The training data is generated from realtime models built in RSCAD. These convolutional layers
specifically designed to extract feature maps from inputs
(F ) using specified convolution kernel (K). Moreover, an
activation function σ(·) offers nonlinearity to the PECNN. The
first convolution layer Cf connected to the input map follows
the forward propagation rule as [15]:
Cf = σ (F ∗ K1,f + Bf )

(5)

where f refers to the f th feature map, ∗ denotes to convolution operator, B is bias. The FC layer is used to generate
the network output OP ECN N by flattening the output from
encoder blocks as:
OP ECN N = σ(Wf c h + Bf c ),

(6)

where Wf c and Bf c are the weight and bias in hidden layers
h, respectively [25].
The input configuration of the network omits specifying
the dimensions, such as height and width, of the input data,
ensuring adaptability to various sizes. Moreover, the proposed
PECNN excludes a pooling layer to avoid the potential loss
of critical information, which is essential for maintaining the
physical relationships among different input channels.
B. Physics-embedded Channel Reformulation
The PECNN offers improved prediction accuracy by the
integration of restructured input channels. Based on MVDC
PF equations (1), six input channels are designed including

Authorized licensed use limited to: Xi'an University of Technology. Downloaded
on July 10,2024 at 07:45:07 UTC from IEEE Xplore. Restrictions apply.
2701

--- page break ---

n×n×6

Output layer

Fully connected layer

Flatten layer

Nfeature,in = 8Nfeature,ini
Nfeature,out = 8Nfeature,ini

Nfeature,in = 2Nfeature,ini
Nfeature,out = 4Nfeature,ini

Input channels

Nfeature,in = Nfeature,ini
Nfeature,out = 2Nfeature,ini

Nfeature,in = Nchannel
Nfeature,out = Nfeature,ini

Physics operation
layer

Xn1 Xn2 ... Xnn

Multi-channel
combination layer

...

...

...

Real-time data

X11 X12 ... X1n
X21 X31 ... X2n

Encoder blocks (two convolutional layers in
each encoder block)
Fig. 1. Proposed PECNN structure for MVDC distribution systems.

voltage, power, current, P/V droop, I/V droop and line conductance channels as:
⎧
CHV = diag(Vdcref m,1 , Vdcref m,1 , ..., Vdcref m,1 )n×n
⎪
⎪
⎪
⎪
⎪
CHP = diag(0, Pdcref m,2 , ..., Pdcref m,m+1 , ..., 0)n×n
⎪
⎪
⎪
⎪
CHI = diag(0, ..., Idcref m,m+2 , .., Idcref m,l+m+1 , ..., 0)n×n
⎪
⎪
⎪
⎨
PV
CHP /V = diag(0, ..., Pdcref m,l+m+2 + Kdroop,l+m+2
Vdcref m,l+m+2 ,
PV
n×n
⎪
+
K
V
..,
P
dcref m,k+l+m+1
⎪
droop,k+l+m+1 dcref m,k+l+m+1 , ..., 0)
⎪
⎪
IV
⎪
⎪
CH
=
diag(0,
...,
I
+
K
×
dcref
m,k+l+m+2
⎪
I/V
droop,k+l+m+2
⎪
⎪
IV
⎪
V
, .., Idcref m,n + Kdroop,n
Vdcref m,n )n×n
⎪
⎪
⎩ dcref m,k+l+m+2
CHG = Gdcm

(7)
However, the potential for information extraction could be
constrained when dealing with a channel that contains less
effective information (fewer number of buses for a specific
bus type). Fewer input channels are required for simplifying
computations in forward/backward information propagations.
The matrices in (7) related to power, P/V droop, and I/V droop
channels are transformed into dc current matrices by:
⎧
rated
Pdcref m,i /Vdcm
⎪
⎪
CHP −−−−−−−−−
−−→ CHIP
⎪
⎪
i=2,...,m+1
⎪
⎨
Pdcref m,i /Vdcref m,i
P /V
CHP /V −−−−−−−−−−−−−→ CHI
⎪
i=l+m+2,...,k+l+m+1
⎪
⎪
⎪
Only keep Idcref m,i
⎪
I/V
⎩ CHI/V −
−−−−−−−−−−−→ CHI

They are then merged with the current matrix CHI in (7)
to create an updated current matrix as (9), hence the six
input channels are now converted into three channels (voltage,
current, conductance).
P /V

I/V

+ CHI

(9)

However, further conversion is required to enhance the
model performance to diverse input network structures. Terminal current Idcm has a linear correlation with the terminal
voltage Vdcm (4), thus (10) can be established for any input
power or current vectors derived from (4) and (8) by splitting
self-conductance and mutual conductance.
merge

Idcm,i =

n


Gdcm,ij · Vdcm,j ,

Vdcm,i =

(10)

j=1

merge
includes accurate and estimated dc current
where Idcm,i
values. Eq. (10) can also be written as (11) to reflect how one

j=i

(11)

Gdcm,ii

The input voltage and current matrices are further reconstructed by (12) and (13), respectively, using matrix Gdcm,ij .
merge,new
Idcm
← Gdcm · diag(Vdcm )
new
Vdcm
←

(12)

merge
) − nondiag(Gdcm ) · diag(Vdcm )
diag(Idcm

diag(Gdcm )

(13)
The reconstructed voltage and current matrices consist of N
dc voltage and current components:
⎤
⎡
Xdcm,11 Xdcm,12 · · · Xdcm,1N
⎢ Xdcm,21 Xdcm,21 · · · Xdcm,2N ⎥
⎥
⎢
..
..
..
..
⎥
⎢
new
=⎢
Xdcm
.
⎥ , (14)
.
.
.
⎥
⎢
⎣ Xdcm,n1 Xdcm,n2 · · · Xdcm,nN ⎦

(8)

i=k+l+m+2,...,n

CHI,total = CHIP + CHI + CHI

node voltage is influenced by its neighbouring node voltage
values.
n

merge
−
Gdcm,ij · Vdcm,j
Idcm,i

component 1

component N

component 2

where X refers to V or I in (12) and (13), respectively. The
sum of all components in each row of (14) is the actual dc
voltage or current values as:
⎧
N
column

⎪
new
new
⎪
Vdcm,iN
⎨
row Vdcm,i =
N =1
(15)
N
column

⎪
⎪
new
new
⎩
I
=
I
dcm,iN
row dcm,i
N =1

In voltage channel CHV , the 2nd to nth diagonal voltage
new
.
elements are substituted by corresponding elements in Vdcm,i

new
CHV i = row Vdcm,i
(i = 2, 3, ..., n).
(16)
In current channel CHI,total , dc current elements in addition
to the elements related to the current buses should be all
updated based on the following rule:
• Voltage bus-related element:

merge,new
CHIi,total = row Idcm,i
(17)
•

Power bus-related elements:
CHIi,total = Pdcref m,i /



new
row Vdcm,i

Authorized licensed use limited to: Xi'an University of Technology. Downloaded
on July 10,2024 at 07:45:07 UTC from IEEE Xplore. Restrictions apply.
2702

(18)

--- page break ---

i=1

l5

TS2

l4

ESS

(a)

no

T7

l7

Conv.3 T3 l

Physics-informed channel
reformulation

Voltage/current channel reformulation

Voltage/current component summation

Matrix element update

5

T8

l6

(b)

yes

T8 T4 Conv.4

TS

l7
l8

l4

Load3 Load4

i≤N

Conv.8

Conv.7

T4

T7

l3

Conv.4

l3

Conv.2 T2

T6

1

l2
Conv.2 T2

l6
T5

DG

l2

TS

l5

T3 Conv.3

Conv.9

l4

T4

Conv.1 T1 l

T6

Conv.8

3

TS1

Conv.6

l2

Conv.2 T2 l

T5

1

DG

l9

T5 Conv.5

T6 Conv.6

l11

l10

T9

T10

(c)

ESS

Conv.10

T3

1

Conv.1 T1 l

Load1 Load2

Load1 Load2

Conv.7

Conv.3

Conv.1 T1 l

Conv.5

Initial new current channel input with voltage and
conductance channels

Input channel
combination

Channel combination of P, I, P/V and I/V channels

Conv.4

Load1 Load2

Conv.6

Conv.5

Start

Fig. 3. MVDC network structures: (a) 6T-MVDC system with load/DG/ESS,
(b) 8T-MVDC system with load, and (c) 9T-MVDC system with
load/DG/ESS.

New voltage/current channels

i=i+1
End

Fig. 2. Physics information embedding process in the proposed PI-FCN for
MVDC distribution systems.
•

P/V bus-related elements:
PV
Pdcref m,i + Kdroop,i
(Vdcref m,i −

CHIi,total =
new
row Vdcm,i

•

I/V bus-related elements:
IV
CHIi,total = Pdcref m,i + Kdroop,i
(Vdcref m,i −



new
row Vdcm,i )

(19)


new
row Vdcm,i )

(20)
The prediction accuracy of the model can be improved
due to the embedded physics principle. Utilizing a single
channel conversion calculation by (12) and (13) yields limited
physics information. By employing multiple conversion calculations, one can obtain adequate physics insights. The complete flowchart illustrating the physics information embedding
process is shown in Fig. 2.
IV. C ASE S TUDY
The proposed PECNN along with other NN models are
developed using PyTorch. Two cases are considered to validate
the superior performance of the proposed PECNN in dc
voltage estimation for MVDC distribution networks compared
to conventional CNN and MLP. All evaluations were conducted on a PC equipped with an Intel(R) Core(TM) i713700K CPU@3.4GHz, 64GB RAM, and a NVIDIA GeForce
RTX 4090 GPU. The two cases include: 1) fixed network
topology that five designed MVDC networks as shown in
Fig. 3(a)-(e) are trained using random sampling of reference
values for grid-connected, DG-connected, ESS-connected, and
load-connected converters; 2) varying network topology that
random line disconnections are considered. The training data
for the designed MVDC systems are obtained from real-time
simulation in RTDS (Fig. 4).

Real-time digital simulator

RSCAD Modelling

(a)

(b)

Fig. 4. Real-time data acquisition: (a) real-time digital simulator, and (b)
modeling in RSCAD.

The initial parameters of converters and lines for the five
networks are listed in Table I. To obtain enough training data,
random sampling for the two cases follows:
• Voltage reference values (p.u.) of all converters are uniformly varied from 0.9 to 1.1.
• For load-connected converters, the power/current reference values (p.u.) uniformly span from 0.8 to 1.2.
• For grid-connected, DG-connected, and ESS-connected
converters, the power/current reference values (p.u.) are
uniformly sampled between 0.9 and 1.1.
• Any single lines/double lines are disconnected at random
considering N − 1 and N − 2 contingency, respectively.
At the same time, the tie switch is closed to maintain
an uninterrupted power flow to the loads, which is integral to the subsequent monitoring of converter outages.
Furthermore, as part of this process, each terminal is
automatically checked during the sampling process to
ensure that no independent terminals are present.
A. Network Modelling
In both the conventional CNN and the proposed PECNN,
six original input channels are converted to three channels
(voltage, current, and conductance), while these three channels
are not reformulated in the conventional CNN. The output
features are set as 64 in the first CNN encoder block, which are
converted to 128, 256, 512 in the following blocks as shown in
Fig. 1. In the encoder and residual blocks, the kernel sizes are
set to 3×3 and 1×1, respectively. The output is produced using
a 1×1 kernel, with both stride s and padding p configured to 1.
Rectified linear unit (ReLU) activation function is adopted in

Authorized licensed use limited to: Xi'an University of Technology. Downloaded
on July 10,2024 at 07:45:07 UTC from IEEE Xplore. Restrictions apply.
2703

--- page break ---

TABLE I
S YSTEM PARAMETERS OF MVDC NETWORKS .
Converter Parameters
Vdcref m (kV),
Pdcref m (MW),
Idcref m (kA)
Control Method
Line Parameters
Distance,
R (Ω/km),
L (mH/km)

Network 1
Network 2
Network 3
Network 1
Network 2
Network 3
Line 1

Converter 1 Converter 2 Converter 3 Converter 4 Converter 5 Converter 6 Converter 7 Converter 8 Converter 9 Converter 10
12, −, −
20, −, −
70, −, −
V
V
V
Line 2

12, 8, −
12, −, -0.6 12, -8, −
12, −, 0.1
12, −, 0
/
/
20, 15, − 20, −, -0.25 20, −, -0.25 20, −, -0.25 20, −, -0.25 20, -5, −
20, -5, −
70, −, 0.7
70, 50, − 70, −, -0.65 70, -45, − 70, −, -0.65 70, −, -0.15 70, -10, −
P/V (8.33)
I
P
I/V (0.35) I/V (0.35)
/
/
P/V (10) I/V (0.2) I/V (0.2)
I
I
P
P
I/V (0.12) P/V (8.57) I/V (0.10) P/V (7.14) I/V (0.10)
P
I
Line 3
Line 4
Line 5
Line 6
Line 7
Line 8
Line 9

1 4, 0.1, 0.02 5, 0.1, 0.02 5, 0.1, 0.02 4, 0.1, 0.02 3, 0.1, 0.02
/
/
2 6, 0.1, 0.02 8, 0.1, 0.02 8, 0.1, 0.02 6, 0.1, 0.02 4, 0.1, 0.02 4, 0.1, 0.02 4, 0.1, 0.02
3 12, 0.1, 0.02 16, 0.1, 0.02 16, 0.1, 0.02 16, 0.1, 0.02 16, 0.1, 0.02 12, 0.1, 0.02 8, 0.1, 0.02

/
/
8, 0.1, 0.02

/
/
8, 0.1, 0.02

/
/
70, −, 0.15
/
/
I/V (0.03)
Line 10

/
/
70, −, 0
/
/
I/V (0.02)
Line 11

/
/
8, 0.1, 0.02

/
/
6, 0.1, 0.02

Note 1: The units of I/V and P/V droop constants are kA/kV and MW/kV, respectively.
Note 2: The listed line distance refers to the distance for each pole.

each convolutional layer. Since MLP only accepts the input of
one-dimensional data, the inputs of an MLP are n dc voltage,
n dc current and n × n conductance values. The used MLP
includes four hidden layers with in total 1000 neurons in all
hidden layers.
A total of 10000 examples are generated to train all NNs
and 1000 resampled data are used to test the network performance. All NNs are trained for 1000 epochs using the
Adam optimizer, with a learning rate of 0.001 and a batch
size of 32. The network loss function employs MSE, and the
prediction accuracy is determined by the proportion of data
deemed qualified to the entire test set. Test data is considered
qualified when the error between the sum of actual MVDC
voltage values predicted by the NNs and the provided samples
is less than a predefined error , expressed as:

 n
n




act(p.u.)
tar(p.u.) 
p.u.
(21)
Vdcm,i
−
Vdcm,i  <.
errorsum = 


i=1

i=1

B. Case 1: Fixed Network Topology
The topology of all MVDC networks remains consistent,
where only the values of converter references, and line resistances are uniformly sampled. The five networks are trained
separately and the prediction accuracy is verified in MLP, CNN
and proposed PECNN. The comparison results are listed in
Table II. The results indicate that the proposed PECNN outperforms other NNs, with its accuracy most notably improving
as the number of iterations increases, especially in the 10TMVDC system.
To further demonstrate the superiority of physics-informed
channel reformulation, a contrast experiment is conducted in
10T-MVDC network as shown in Fig. 5. Three NNs are
used in the contrast experiment, including MLP, CNN and
PECNN (PECNN refers to PECNN with 20 iterations in the
subsequent description), to assess their performance based
p.u.
. Fig. 5(a) and
on MVDC voltage prediction errors errorsum
Fig. 5(b) show the prediction accuracy comparison when
the dc power/current references of load-connected converters
ranges from 0.3 to 1.7 and dc power/current references of
grid-connected converters change from 0.7 to 1.3, respectively.
The proposed PECNN still has higher prediction accuracy in
untrained areas, although all three NNs have good performance
in trained areas.

TABLE II
P REDICTION ACCURACY COMPARISON OF DIFFERENT NN S UNDER
C ASE 1.
Neural Network

6T-MVDC

8T-MVDC

10T-MVDC

MLP
CNN
PECNN (1 iteration)
PECNN (20 iterations)

95.8%
94.6%
99.5%
99.7%

91.4%
92.2%
98.0%
99.0%

88.2%
87.9%
97.8%
98.5%

1.4

0.6

1.2

0.5

1

0.4

0.8

0.3

0.6

0.2

0.4

0.1

0.2

0
0.3 0.5

0.7 0.9

1.1 1.3

1.5 1.7

0
0.7

0.8

0.9

1

1.1

1.2

1.3

Fig. 5. Prediction error comparison for 10T-MVDC distribution system
under different NNs: (a) dc power/current reference value changes of loadconnected converters, and (b) dc power/current reference value variations of
grid-connected converters.

C. Case 2: Varying Network Topology with Random Line
Disconnection
Random line disconnection is included in this case in
addition to the uniform sampling of converter references and
line resistances. Single and double line disconnections are
considered together to mimic N − 1 and N − 2 contingencies.
Table III lists the prediction accuracy considering random
single and double line disconnections in the five MVDC
systems. The prediction accuracy of MLP and conventional
CNN declines compared to fixed topology due to the increased
training complexity for untrained topology structures. However, the proposed PECNN also maintains good performance
in such case, despite a slight decrease in prediction accuracy.
In addition, a test for generalization capability is conducted,
wherein the system is trained on single line disconnections and
then tested on double line disconnections (N −2 contingency).
Fig. 6 presents a detailed comparison of prediction errors,
examining the effects of single-line disconnection (line 1) and
concurrent disconnections of line 1 & line 3, within the 10TMVDC system. The proposed PECNN outperforms others in

Authorized licensed use limited to: Xi'an University of Technology. Downloaded
on July 10,2024 at 07:45:07 UTC from IEEE Xplore. Restrictions apply.
2704

--- page break ---

line 1 & line 3
disconnection
line 1
(unseen)
disconnection

0.05

0.1

0.15

0.2

0.25

0.3

0.35

0

Fig. 6. Prediction error comparison for random line disconnection occurred
in 10T-MVDC distribution system under different NNs.

both single and unseen double line tripping scenarios, owing
to its integration of physics-based information.
TABLE III
P REDICTION ACCURACY (%) COMPARISON OF DIFFERENT NN S UNDER
C ASE 2 - LINE DISCONNECTION .
Neural Network

6T-MVDC

8T-MVDC

10T-MVDC

MLP
CNN
PECNN (20 iterations)

86.8%
90.8%
99.4%

82.8%
88.3%
98.5%

78.6%
83.5%
98.1%

V. C ONCLUSION
This paper proposes a novel PECNN with integrated physics
guidance to predict terminal dc voltage in MT-MVDC distribution networks, addressing the accuracy reduction issue
in conventional NNs under unseen data distributions and
topology structures. The PECNN simplifies its structure by
merging various MVDC bus-type inputs into three channels
using a channel combination layer. This reduces the NN
computation burden and strengthens the feature extraction
capability of PECNN by information concentration across
different channels. In the presented physics-informed channel
reformulation method, the intrinsic physical relation between
voltage, current, and conductance in an MVDC network is
embedded by reconstructing the input voltage and current
matrices. It allows a more thorough extraction of information,
elevates prediction accuracy and strengthens generalization
capability.
ACKNOWLEDGMENT
The work was supported under Australian Research Council’s Discovery Project (DP210102294), the Digital Finance
Cooperative Research Centres (CRC) program, an Australian
Government initiative, and IRC for Sustainable Energy Systems at KFUPM under project # INSE2415.
R EFERENCES
[1] CIGRE WG C6/B4.37, “Medium voltage DC distribution systems,”
CIGRE, Tech. Brochure 875, Jul. 2022.
[2] P. Sun, Y. Tian, J. Pou, and G. Konstantinou, “Beyond the MMC:
Extended modular multilevel converter topologies and applications,”
IEEE Open J. Power Electron., vol. 3, pp. 317–333, May 2022.
[3] Y. Ji, Z. Yuan, J. Zhao, C. Lu, Y. Wang, Y. Zhao, Y. Li, and Y. Han, “Hierarchical control strategy for MVDC distribution network under large
disturbance,” IET Generation, Transmission & Distribution, vol. 12,
no. 11, pp. 2557–2565, May 2018.

[4] P. Sun, R. Wu, G. Li, M. Khalid, G. Town, and G. Konstantinou,
“Decoupled sequential power flow study in MT-MVDC distribution
systems based on novel NR/estimation-correction algorithm,” in 2023
11th Int. Conf. Power Electron. ECCE Asia (ICPE 2023 - ECCE Asia),
May 2023, pp. 1464–1469.
[5] M. Karimi et al., “Application of Newton-based load flow methods for
determining steady-state condition of well and ill-conditioned power
systems: A review,” Int. J. of Elect. Power & Energy Syst., vol. 113,
pp. 298–309, Dec. 2019.
[6] O. I. Abiodun, A. Jantan, A. E. Omolara, K. V. Dada, N. A. Mohamed,
and H. Arshad, “State-of-the-art in artificial neural network applications:
A survey,” Heliyon, vol. 4, no. 11, 2018.
[7] P. Simiyu, A. Xin, K. Wang, G. Adwek, and S. Salman, “Multiterminal
medium voltage DC distribution network hierarchical control,” Electronics, vol. 9, no. 3, Mar. 2020.
[8] V. Paucar and M. J. Rider, “Artificial neural networks for solving the
power flow problem in electric power systems,” Elect. Power Syst. Res.,
vol. 62, no. 2, pp. 139–144, Jun. 2002.
[9] X. Hu, H. Hu, S. Verma, and Z.-L. Zhang, “Physics-guided deep neural
networks for power flow analysis,” IEEE Trans. Power Syst., vol. 36,
no. 3, pp. 2082–2092, May 2021.
[10] W. Dong, Z. Xie, G. Kestor, and D. Li, “Smart-pgsim: Using neural
network to accelerate ac-opf power grid simulation,” in Int. Conf. High
Perform. Comput., Netw., Storage Anal., Nov. 2020, pp. 1–15.
[11] X. Pan, T. Zhao, M. Chen, and S. Zhang, “DeepOPF: A deep neural
network approach for security-constrained DC optimal power flow,”
IEEE Trans. Power Syst., vol. 36, no. 3, pp. 1725–1735, May 2021.
[12] M. K. Singh, V. Kekatos, and G. B. Giannakis, “Learning to solve the
AC-OPF using sensitivity-informed deep neural networks,” IEEE Trans.
Power Syst., vol. 37, no. 4, pp. 2833–2846, Jul. 2022.
[13] X. Pan, M. Chen, T. Zhao, and S. H. Low, “DeepOPF: A feasibilityoptimized deep neural network approach for AC optimal power flow
problems,” IEEE Syst. J., vol. 17, no. 1, pp. 673–683, Mar. 2023.
[14] R. Khalitov, T. Yu, L. Cheng, and Z. Yang, “Chordmixer: A scalable
neural attention model for sequences with different lengths,” 2023.
[15] Z. Li, F. Liu, W. Yang, S. Peng, and J. Zhou, “A survey of convolutional
neural networks: Analysis, applications, and prospects,” IEEE Trans.
Neural Netw. Learn. Syst., vol. 33, no. 12, pp. 6999–7019, Jun. 2022.
[16] Y. Zhou, W.-J. Lee, R. Diao, and D. Shi, “Deep reinforcement learning
based real-time AC optimal power flow considering uncertainties,”
Journal of Modern Power Systems and Clean Energy, vol. 10, no. 5,
pp. 1098–1109, Sep. 2022.
[17] Y. Du, F. Li, J. Li, and T. Zheng, “Achieving 100x acceleration for N-1
contingency screening with uncertain scenarios using deep convolutional
neural network,” IEEE Trans. Power Syst., vol. 34, no. 4, pp. 3303–3305,
Jul. 2019.
[18] Y. Jia and X. Bai, “A CNN approach for optimal power flow problem
for distribution network,” in 2021 Power System and Green Energy
Conference (PSGEC). IEEE, Aug. 2021.
[19] Y. Jia, X. Bai, L. Zheng, Z. Weng, and Y. Li, “ConvOPF-DOP: A datadriven method for solving AC-OPF based on CNN considering different
operation patterns,” IEEE Trans. Power Syst., vol. 38, no. 1, pp. 853–
860, Jan. 2023.
[20] D. Wang, K. Zheng, Q. Chen, X. Zhang, and G. Luo, “A datadriven probabilistic power flow method based on convolutional neural
networks,” International Transactions on Electrical Energy Systems,
vol. 30, no. 7, p. e12367, Mar. 2020.
[21] F. Aksan, Y. Li, V. Suresh, and P. Janik, “CNN-LSTM vs. LSTM-CNN
to predict power flow direction: A case study of the high-voltage subnet
of northeast germany,” Sensors, vol. 23, no. 2, p. 901, Jan. 2023.
[22] G. E. Karniadakis, I. G. Kevrekidis, L. Lu, P. Perdikaris, S. Wang, and
L. Yang, “Physics-informed machine learning,” Nature Reviews Physics,
vol. 3, no. 6, pp. 422–440, May 2021.
[23] P. Sun, R. Wu, Z. Shen, G. Li, M. Khalid, G. Town, and G. Konstantinou,
“Sequential power flow algorithm and post-event steady-state power
distribution analysis in hybrid AC/MT-MVDC systems,” Int. J. of Elect.
Power & Energy Syst., vol. 157, p. 109828, Jun. 2024.
[24] S. Gao, Y. Chen, S. Huang, and Y. Xia, “Efficient power flow algorithm
for AC/MTDC considering complementary constraints of VSC’s reactive
power and AC node voltage,” IEEE Trans. Power Syst., vol. 36, no. 3,
pp. 2481–2490, May 2021.
[25] K. O’Shea and R. Nash, “An introduction to convolutional neural
networks,” 2015.

Authorized licensed use limited to: Xi'an University of Technology. Downloaded
on July 10,2024 at 07:45:07 UTC from IEEE Xplore. Restrictions apply.
2705

--- page break ---
