# A Physics-informed Neural Network Method for LC Parameter Estimation in Three-Phase Inverter

> Derived Markdown text extracted from the PDF for ingestion.
> The PDF under `raw/` remains the source of truth.

- source_id: `kong_2024_pinn_lc_parameter_estimation`
- raw_pdf: `raw/kong_2024_pinn_lc_parameter_estimation/Kong et al_2024_A Physics-informed Neural Network Method for LC Parameter Estimation in.pdf`

## Extracted Text

2024 IEEE 10th International Power Electronics and Motion Control Conference (IPEMC2024-ECCE Asia) | 979-8-3503-5133-0/24/$31.00 ©2024 IEEE | DOI: 10.1109/IPEMC-ECCEAsia60879.2024.10567996

A Physics-informed Neural Network Method for LC
Parameter Estimation in Three-Phase Inverter
Jie Kong, Dao Zhou, Xing Wei, and Huai Wang
AAU Energy, Aalborg University, Denmark
Email: {jiek, zda, xwe, hwa}@energy.aau.dk
Abstract—The DC-link capacitance and the AC-side
inductance parameters can be used as feedback for control
optimization and component degradation monitoring. This
paper proposes a parameter estimation method based on the
combination use of artificial neural network and circuit
analytical models, e.g., physics-informed neural network
(PINN), for a three-phase inverter application. It does not
require any additional hardware circuitry and can be welltrained based on a small training dataset. A three-phase
inverter case study is presented with theoretical analyses,
simulations, and experimental verifications. The results show
that satisfactory accuracy can be achieved for the estimation
of DC-link capacitance and AC-side inductance parameters.
Index Terms— Parameter estimation, capacitor, inductor,
condition monitoring, physics-informed neural network,
three-phase inverter.

I. INTRODUCTION
Condition monitoring and degradation prognostics play
a significant role in enhancing the reliability of power
electronic systems. The main reason that the power
electronic converter performance cannot fulfill the lifespan
requirement lies in the degradation of critical vulnerable
components [1]. Parameter estimation for a power
electronic system serves as a valuable tool for degradation
monitoring and predictive maintenance. Reliability
analysis methods can be divided into model-based and
data-driven approaches. In model-based reliability
approaches, mathematical models or differential equations
are constructed to represent the underlying physics,
degradation process, and failure modes of power electronic
systems. Data-driven methods are particularly useful when
detailed knowledge of the system's underlying physics or
failure mechanisms may be lacking or difficult to model
accurately. A non-invasive parameter estimator is
presented in [3], which can simultaneously predict both the
circuit and control parameters of a voltage source
converter (VSC). It serves as a valuable resource for
failure diagnosis and preventive maintenance. In [3], a
feed-forward neural network is proposed to establish the
nonlinear relationship between the dc-link capacitor's
capacitance and the harmonics of its ripple voltage. This
trained neural network can deduce the capacitor's
capacitance indirectly from the ripple voltage harmonics.
The data-driven approach can learn and extract valuable
insights from the system by leveraging high-quality
monitoring data. However, the power electronic system is
currently not a data-intensive field, and high-quality data
is difficult to access, accelerated life test usually takes a

very long time. In recent years, the advent of digital twin
(DT) and artificial intelligence (AI) has revolutionized
various fields, including the major field power electronics
[4] , [5]. For prior-art studies, a digital twin approach for
identifying degradation parameters was experimentally
demonstrated in a DC/DC buck converter [6], a DC/DC
boost converter [7], and a single-phase DC/AC inverter [8],
respectively. Therefore, the hybrid approaches, especially
the AI methods integrated with physical principles, have
become a new paradigm for accurate modeling and robust
parameter estimation [9].
To bridge the gap between data-driven techniques and
physics-based modeling, a novel approach known as
physics-informed machine learning has emerged [10], [11].
The advancements of these techniques are explored in [12],
and the potential benefits of combining physics-informed
approaches with machine learning techniques for
predictive maintenance tasks in power electronic
converters are discussed in detail. The first physicsinformed neural network (PINN) approach in the power
electronic domain focuses on non-invasive parameter
estimation of a buck converter, in which the PINN model's
robustness is evaluated by comparing simulation with
experimental data [13]. This paper aims to extend the
application of the PINN concept in [13] to a three-phase
inverter. The new challenge lies in the increased order of
physical equations, operation modes, and number of
circuit parameters.
The rest of the paper is organized as follows: Section II
presents the methodology and the formulation of the PINN
model for parameter estimation. Section III describes the
results and discusses the simulation and the experimental
setup used for the validation. Section IV concludes this
work and summarizes future research directions.
II. MODELING OF THREE-PHASE INVERTER WITH
PINN
A. Inverter dynamic model
In this paper, a three-phase full-bridge inverter is
investigated by using the bipolar sinusoidal pulse width
modulation (SPWM), the circuit topology of which is
shown in Fig. 1. DC/AC converter is widely used in power
electronics systems, including electric vehicles,
uninterruptible power supplies, photovoltaic and wind
power systems. Considering the voltage and current
balance of a three-phase circuit, the dynamic equation of
the inverter can be derived as (1):

979-8-3503-5133-0/24/$31.00 ©2024 IEEE
Authorized licensed use limited to: Xi'an University of Technology. Downloaded
on July 10,2024 at 07:38:28 UTC from IEEE Xplore. Restrictions apply.
3957

--- page break ---

iin
VT1

VT3

VT5

Uin
A
B

Udc

C
RL

VT2

VT4

ia

La

ib

Lb Rb

ic

Lc Rc

Ra
O

VT6

N

Fig. 1. The configuration of three-phase DC/AC inverter.

dia
+ Ra ia = v AN + vNO
dt
di
Lb b + Rbib = vBN + vNO
dt
dic
Lc
+ Rc ic = vCN + vNO
dt
dv
C dc = iin − ( S a ia + Sbib + S cic )
dt
U in = RL iin + vdc

grid search method. The optimizer in Fig. 2 is responsible
for estimating both the hyperparameters of the neural
network and the parameters of the underlying physical
circuit model. The combination of Adam optimizer and LBFGS optimizer [14] is used to train the neural network,
which can improve the PINN solution across a variety of
network sizes.
The differential equations governing the dynamics of
any given system can be expressed in the general form of
nonlinear partial differential equations (PDEs) as follows
[10]:

ut + N u;   = 0, x , t  [0, T ]; f := ut + N u;  

La

1
[𝑅 𝑖 − (𝑣𝐴𝑁 + 𝑣𝑁𝑂 )]
𝐿𝑎 𝑎 𝑎
1
𝒩[𝑖𝑏 ; 𝜆] = [𝑅𝑏 𝑖𝑏 − (𝑣𝐵𝑁 + 𝑣𝑁𝑂 )]
𝐿𝑏
1
𝒩[𝑖𝑐 ; 𝜆] = [𝑅𝑐 𝑖𝑐 − (𝑣𝐶𝑁 + 𝑣𝑁𝑂 )]
𝐿𝑐
1
[𝑖 − (𝑆𝑎 𝑖𝑎 + 𝑆𝑏 𝑖𝑏 + 𝑆𝑐 𝑖𝑐 )]
𝒩[𝑖𝑖𝑛 ; 𝜆] =
𝐶𝑅𝐿 𝑖𝑛
𝒩[𝑖𝑎 ; 𝜆] =

(1)

1
vNO = − (v AN + vBN + vCN )
3
v AN = S a vdc
vBN = Sb vdc
vCN = S c vdc
where 𝑖𝑎 , 𝑖𝑏 , 𝑖𝑐 are the three-phase inductor currents,
𝑣𝑑𝑐 is the DC-link voltage, 𝑖𝑖𝑛 is the input current from
the DC source. 𝐿𝑎 , 𝐿𝑏 , 𝐿𝑐 , are the inductance of threephase inductor. 𝑅𝑎 , 𝑅𝑏 , 𝑅𝑐 are the resistive load
including the parasitic resistance of three-phase inductor.
𝐶 is the capacitance of the DC-link capacitor, 𝑅𝐿 is the
internal resistance of power source. Each phase arm has
two switches operated in complementary. 𝑆𝑎 , 𝑆𝑏 , 𝑆𝑐 stand
for the state of the top switches in each phase. In this case,
the conduction is carried out either by the power switches
or the diode, depending on the direction of the phase
current.
B. Implementation of PINN
The basic structure of the PINN is shown in Fig. 2. It
comprises two main parts: the data-driven part and the
physical model part. In the PINN, the deep neural network
represents the data-driven part. In this study, the
parameters of the passive components are considered. The
design of neural networks involves selecting appropriate
numbers of layers and neurons. A suitable network
structure should possess sufficient expressiveness to
model intermediate states effectively, while avoiding
excessive complexity that could inflate training time and
costs. A neural network with 7 layers and 50 neurons in
each layer is applied in the data-driven part through the

(2)

For the parameter estimation of a three-phase inverter,
𝒩[𝑢; 𝜆] is the PDEs defining the dynamic characteristics
of the inverter, 𝑢 can be either the phase current 𝑖𝑎 , 𝑖𝑏 ,
𝑖𝑐 or the input current 𝑖𝑖𝑛 . λ is the circuit parameter set to
be estimated including 𝐿𝑎 , 𝐿𝑏 , 𝐿𝑐 , 𝐶. The latent state
predicted by the neural network, is constrained by 𝑓 ,
which can combine the neural network with the physical
model.
As depicted in Fig. 3, in the case that the state
variables 𝑢(𝑡𝑛 ) and 𝑢(𝑡𝑛+1 ) are available and
measurable, u represents either the current or the voltage
of the inverter. The time interval between 𝑡𝑛 and 𝑡𝑛+1
are defined as 𝑡𝑛+1 = 𝑡𝑛 + 𝑐𝑖 ∆𝑡, where 𝑐𝑖 is a coefficient
ranging from 0 to 1. The discretization method assumes
that the 𝑞 stage latent state between 𝑡𝑛 and 𝑡𝑛+1 are
unobservable and can be predicted based on the neural
network. The backward equation (3) and forward equation
(4) are the general form of the implicit Runge-Kutta
method, (𝑎𝑖𝑗 , 𝑏𝑗 , 𝑐𝑗 ) is constant parameters, where the
details are discussed in previous study [13].
𝑞

𝑢𝑖 (𝑡𝑛 ) = 𝑢(𝑡𝑛+𝑐𝑖 ) + ∆𝑡 ∑ 𝑎𝑖𝑗 𝒩 [𝑢 (𝑡𝑛+𝑐𝑗 ) ; 𝜆]

(3)

𝑗=1
𝑞

𝑢𝑖 (𝑡𝑛+1 ) = 𝑢(𝑡𝑛+𝑐𝑖 ) + ∆𝑡 ∑(𝑎𝑖𝑗 − 𝑏𝑗 )𝒩 [𝑢 (𝑡𝑛+𝑐𝑗 ) ; 𝜆] (4)
𝑗=1

Authorized licensed use limited to: Xi'an University of Technology. Downloaded
on July 10,2024 at 07:38:28 UTC from IEEE Xplore. Restrictions apply.
3958

--- page break ---

Latent
State

Physical Backward
Model Equation Output

Artificial Neural Network

Input

ib (tn )
ic (tn )

iˆa (t n )
iˆb (t n )
iˆc ( t n )

iin (tn )

iˆin (tn )

Sa

iˆa (tn 1)

Sb

iˆb (tn 1)

Sc

iˆc (tn 1 )

t

iˆin (tn 1)

ia (tn )

7 layers and 50 neurons each layer

Forward
Equation

Circuit
parameters
Optimiser
(Adam+L-BFGS)

NN parameters

Loss
Function

Fig. 2. The basic architecture of PINN, which comprises the data-driven part and the physical model part.

These equations are used to couple the latent state data
with the observable state data in the physical model part.
The physical constraint can reduce the solution space,
which is the advantage of the PINN method. This
constraint-based approach contributes significantly to
reducing the solution space, enhancing the accuracy and
efficiency of parameter estimation.
1

Carrier

Modulation

Uc_ref
Ua_ref

0

Ub_ref
-1
1
0
1
0
1

Sb

)

(

) (

)

(

) (

)

(

) (

(5)

)

2
2
+   iin (tn ) − iˆin (tn ) + iin (tn +1 ) − iˆin (tn +1 ) 


n 

where the parameter set is denoted by Θ = {w, b, θ}, where
{w, b} represent the weights and biases associated with the
data-driven part of PINN. On the other hand, θ refers to the
parameters defining the physical model of the inverter.

Sc

tn 1

tn

III. SIMULATION AND EXPERIMENTAL
VALIDATION

Forward Equation

tn

) (

2
2
+   ic (tn ) − iˆc (tn ) + ic (tn +1 ) − iˆc (tn +1 ) 


n 

(a) SPWM modulation

u (tn )

(

2
2
+   ib (tn ) − iˆb (tn ) + ib (tn +1 ) − iˆb (tn +1 ) 



n

Sa

0

The input of the neural network is the three-phase initial
current states 𝑖𝑎 (𝑡𝑛 ), 𝑖𝑏 (𝑡𝑛 ) ,𝑖𝑐 (𝑡𝑛 ) , 𝑖𝑖𝑛 (𝑡𝑛 ) , top switch
state in each phase 𝑆𝑎 , 𝑆𝑏 , 𝑆𝑐 , and each period ∆𝑡 when
the switch state combination changes. The output of the
neural network is the 𝑞 stage latent state ( 𝑞 = 20 )
between 𝑡𝑛 and 𝑡𝑛+1 . The output of the physical model
is the initial and ending current states 𝑖̇̂𝑎 (𝑡𝑛 ), 𝑖̇̂𝑏 (𝑡𝑛 ),
𝑖̇̂𝑐 (𝑡𝑛 ), 𝑖̇̂𝑖𝑛 (𝑡𝑛 ), 𝑖̇̂𝑎 (𝑡𝑛+1 ), 𝑖̇̂𝑏 (𝑡𝑛+1 ), 𝑖̇̂𝑐 (𝑡𝑛+1 ), 𝑖̇̂𝑖𝑛 (𝑡𝑛+1 ) .
The loss function of the PINN is formulated as (5):
2
2
E () =   ia (tn ) − iˆa (tn ) + ia (tn +1 ) − iˆa (tn +1 ) 



n

u(tn c2 )

u(tn c1 )
c1 t

tn

u(tn c3 )

c2 t tn

u(tn cq )
tn

c3 t

u (tn 1 )

cq t

Backward Equation

t
(b) Time-stepping scheme
Fig. 3. The implicit Runge-Kutta discretization method. This setting
applies to state variables including the current and the voltage.

In this section, the proposed PINN model of the inverter
is verified through both simulation and experimental
hardware. The specification of the key components of the
inverter is listed in Table Ⅰ. The peak-to-peak sampling
method reduces the sampling frequency to 6𝑓𝑠𝑤 in the
inverter, where 𝑓𝑠𝑤 is the switching frequency. The
simulation model is consistent with the key parameters of
the experimental prototype, which is measured offline by

Authorized licensed use limited to: Xi'an University of Technology. Downloaded
on July 10,2024 at 07:38:28 UTC from IEEE Xplore. Restrictions apply.
3959

--- page break ---

TABLE I
SPECIFICATIONS OF THE THREE-PHASE DC/AC INVERTER
𝑼𝒊𝒏
𝒇𝒐
𝒇𝒔𝒘
𝑪
𝑳𝒂

TABLE II
PERCENTAGE ERROR (%) OF COMPONENT PARAMETERS
Error (%)

Mean

𝑳𝒂

𝑳𝒃

𝑳𝒄

𝑪

200𝑉

Clean data
ADC error
Random noise
Sync error
ADC-Sync-10
noise

0.45
0.73
0.96
5.38
5.80

0.19
0.26
0.76
0.10
0.54

0.84
0.94
0.52
16.95
16.35

0.64
0.76
0.51
0.61
0.48

0.12
0.94
2.03
4.46
5.81

50𝐻𝑧

2𝑘𝐻𝑧

717.3𝜇𝐹

3.79𝑚𝐻

𝑳𝒃

𝑳𝒄

𝑹𝒂

𝑹𝒃

𝑹𝒄

3.83𝑚𝐻

3.74𝑚𝐻

60.3𝑚Ω

63.5𝑚Ω

55.3𝑚Ω

the LCR meter. The data are collected from simulation and
are pre-processed to obtain the PINN backward and
forward dataset.
The efficacy of condition monitoring in field
applications can be affected by various sources of signal
measurement and sensing errors. These errors can arise
from different stages throughout the data collection
pipeline. Measurement uncertainties during the data
acquisition process include sensor linearity errors in
analog signal reconstruction, quantization errors, DC
offset errors, and synchronization errors in Analog-todigital converter (ADC) conversion.

(a) Convergence of the training loss through equation (5)

Quantization error includes amplitude and time
quantization, caused by the limited number of bits of ADC
and limited sampling frequency, respectively. The
amplitude quantization error is emulated by adding ADC
error to emulate the quantization process of a 12-bit ADC.
Synchronization errors are due to delays in hardware
circuits and sensing process. Therefore, a random period
[0, 20] us is incorporated to emulate synchronization error,
and random noise (10 times ADC error) is introduced into
the signals. The synchronization error occurs during the
sampling of the signals of 𝑖𝑏 and 𝑖𝑖𝑛 . Different
combinations of the disturbance factors have been
evaluated. The ADC-Sync-10 noise means the three kinds
of noise are incorporated at the same time, and the
outcomes are presented in Table II.
As illustrated in Fig. 4 (a), the convergence process in
the case of clean data in Table II is presented in a
logarithmic scale. Fig. 4 (b) and (c) also demonstrate the
convergence of the inductance value 𝐿𝑎 and the DC link
capacitance 𝐶, the circuit parameters eventually stabilize
around the true values after multiple learning iterations
during the training process. It is observed that after the
5000th iteration, the estimated parameters start to converge
to the measurement values.

(b) Process of parameter 𝐿𝑎 convergence
(a) Current state 𝑖𝑎 (𝑡𝑛 ) for backward dataset

(c) Process of parameter 𝐶 convergence
Fig. 4. Convergence of the training process of the PINN. The epoch
of the Adam optimizer is set as 200 000 and the following L-BFGS
optimizer is set as 70000. La is the inductance of inductor in phase A. C
is the DC link capacitance.

(b) Current state 𝑖𝑎 (𝑡𝑛+1 ) for forward dataset
Fig. 5. Current waveform prediction for backward and forward datasets,
taking the inductor current in phase A as an example.

Authorized licensed use limited to: Xi'an University of Technology. Downloaded
on July 10,2024 at 07:38:28 UTC from IEEE Xplore. Restrictions apply.
3960

--- page break ---

Comparing the waveform prediction results with the
simulation results for backward and forward datasets, it is
evident that the predicted current waveform closely tracks
the simulation current state, as shown in Fig. 5. The load
change is realized to change the current reference value in
the process of data acquisition. The predicted current
waveform and the simulated current waveform of phase A
are basically the same under different load conditions.
Moreover, Table II shows that the ADC error slightly
influences the estimation accuracy of LC parameters. The
main cause is that ADC quantization error primarily
impacts the peak value of the inductor current while
exerting minimal influence on the slope of the inductor
current or the RC time constant for the voltage waveform.
At the same time, the synchronization error has a
significant impact on the accuracy of the inductance
prediction results. The relative error of 𝐿𝑏 prediction in
phase B is 16.95% when the synchronization error is
introduced in the acquisition of the current of the inductor.
Furthermore, the parameter of the capacitor is affected to
a relatively small extent, with the prediction error being
approximately 4.46%. The inverter hardware prototype is
shown in Fig. 6. The maximum power rating is designed

to be 5kW. The PLECS RT Box 2 [15] is used as the
controller. The voltage and current sensor errors are
reduced by linear calibration during the experiments. The
experimental backward and forward dataset is collected by
RT Box 2 during the inverter's operation. The training
process for the PINN is accomplished on a CPU platform
Intel(R) Core i5-1135G7@ 2.40GHz. Notably, the method
showcases a data-light characteristic. A small dataset
comprising only 360*3 data samples for each state variable
is used. The dataset preparation makes it easily achievable
in practical applications. The proposed method is repeated
10 times in the same dataset to show the variations of
estimated results, while the load change dataset is
measured only once. The identified parameters in the
experiment are shown in Fig. 7. It can be observed that the
prediction performance of the proposed PINN model is
stable, which demonstrates a maximum discrepancy of 5.2%
for the DC-link capacitance and 14.7% for the AC-side
inductance. In the process of hardware experiment, due to
the limited sampling rate, there is a relatively large
synchronization error when the voltage and current signals
are sampled and stored.

(a) Hardware platform

RL Loads

Auxiliary Power Supply

DC-link Capacitor

DC Power Supply

Zoom in

Sensor and sampling board

3-phase Inverter

RT Box

Zoom in

(b) Experimental data acquisition
Fig. 6. The experimental prototype and data acquisition.

Authorized licensed use limited to: Xi'an University of Technology. Downloaded
on July 10,2024 at 07:38:28 UTC from IEEE Xplore. Restrictions apply.
3961

--- page break ---

Fig. 7. Parameter estimation results based on experimental testing data.

According to the previous analysis, the synchronization
error has a significant impact on the accuracy of parameter
estimation. Therefore, the accuracy of the parameter
estimation results can be further improved by
compensating for the synchronization error of the
acquisition process or by further designing the real-time
trigger sampling pattern.
IV. CONCLUSIONS
This paper aims to extend our previously proposed
method in [13] for the three-phase inverter. The applied
physics-informed neural network (PINN) retains the
advantages of significantly reduced efforts in training data
preparation and efficient computation based on ultra-small
data. The complexity level of the differential equations and
the number of circuit variables are increased in the threephase inverter compared to the Buck converter studied in
[13]. An error analysis is performed for both simulation
data with intentionally introduced measurement errors and
experimentally measured data. Based on the experimental
test it shows a maximum error of 5.2% and 14.7% for the
DC-link capacitance and AC-side inductance, respectively.
This work highlights the potentials and opportunities that
arise from merging physics with data-driven methods in
the field of power electronics.

IEEE Trans. Power Electron., vol. 36, no. 4, pp. 4633–4658,
Apr. 2021.
[5] Z. Lei, H. Zhou, X. Dai, et al. Digital Twin Based
Monitoring and Control for DC-DC Converters. Nat.
Commun., vol. 14, no. 5604, 2023.
[6] Y. Peng, S. Zhao, and H. Wang, "A Digital Twin based
Estimation Method for Health Indicators of DC-DC
Converters," IEEE Trans. Power Electron., vol. 36, no. 2,
pp. 2105–2118, Feb. 2021.
[7] G. D. Nezio, M. d. Benedetto, A. Lidozzi and L. Solero,
"DC-DC Boost Converters Parameters Estimation Based on
Digital Twin," IEEE Trans. Ind. Appl., vol. 59, no. 5, pp.
6232-6241, Sep./Oct. 2023.
[8] Q. Wu, W. Wang, et al., "Digital Twin Approach for
Degradation Parameters Identification of a Single-Phase
DC-AC Inverter," 2022 IEEE Applied Power Electronics
Conference and Exposition (APEC), pp. 1725-1730, 2022.
[9] O. Fink, Q. Wang, M. Svensén, et al., "Potential, Challenges
and Future Directions for Deep Learning in Prognostics and
Health Management Applications," Eng. Appl. Artif. Intel.,
vol. 92, 2020.
[10] M. Raissi, P. Perdikaris, and G. E. Karniadakis, "PhysicsInformed Neural networks: A Deep Learning Framework
for Solving Forward and Inverse Problems Involving
Nonlinear Partial Differential Equations," J. Computational
Physics, vol. 378, pp. 686–707, Feb. 2019.
[11] G. E. Karniadakis, I. G. Kevrekidis, L. Lu, P. Perdikaris, S.
Wang, and L. Yang, "Physics-Informed Machine Learning,"
Nat. Rev. Phys., vol. 3, no. 6, pp. 422–440, May 2021.
[12] Y. Fassi, V. Heiries, J. Boutet and S. Boisseau, "Toward
Physics-Informed Machine-Learning-Based Predictive
Maintenance for Power Converters—A Review," IEEE
Trans. Power Electron., vol. 39, no. 2, pp. 2692-2720, Feb.
2024.
[13] S. Zhao, Y. Peng, Y. Zhang, and H. Wang, "Parameter
Estimation of Power Electronic Converters with PhysicsInformed Machine Learning," IEEE Trans. Power Electron.,
vol. 37, no. 10, pp. 11567–11578, 2022.
[14] P. Rathore, W. Lei, Z. Frangella, L. Lu, and M. Udell,
"Challenges in Training Pinns: A Loss Landscape
Perspective. " arXiv preprint arXiv:2402.01868, 2024.
[15] PLEXIM, PLECS RT Box 2, accessed on Oct. 5, 2023,
[Online]. Available: https://www.plexim.com/

REFERENCES
[1] S. Rahimpour, H. Tarzamni, et al., "An Overview of
Lifetime Management of Power Electronic Converters,"
IEEE Access, vol. 10, pp. 109688-109711, 2022.
[2] B. H. Lin, J. T. Tsai and K. L. Lian, "A Non-Invasive
Method for Estimating Circuit and Control Parameters of
Voltage Source Converters," IEEE Trans. Circuits Syst. I
Reg. Papers, vol. 66, no. 12, pp. 4911-4921, 2019.
[3] H. Soliman, I. Abdelsalam, H. Wang, and F. Blaabjerg,
"Artificial Neural Network Based DC-link Capacitance
Estimation in a Diode-bridge Front-end Inverter System,"
Proc. IEEE 3rd Int. Future Energy Electron. Conf., pp. 196–
201, 2017.
[4] S. Zhao, F. Blaabjerg, and H. Wang, "An Overview of
Artificial Intelligence Applications for Power Electronics,"

Authorized licensed use limited to: Xi'an University of Technology. Downloaded
on July 10,2024 at 07:38:28 UTC from IEEE Xplore. Restrictions apply.
3962

--- page break ---
