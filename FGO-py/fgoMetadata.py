classCorrection=[ # 攻击补正 集星权 掉星率 克制关系
[1.0, 100,10/100,[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0]],
[1.0, 100,10/100,[1.0,1.0,0.5,2.0,1.0,1.0,1.0,2.0,0.5,1.0,1.0,1.0,1.0,1.0,0.5]],
[0.95,150,8/100, [1.0,2.0,1.0,0.5,1.0,1.0,1.0,2.0,0.5,1.0,1.0,1.0,1.0,1.0,0.5]],
[1.05, 90,12/100,[1.0,0.5,2.0,1.0,1.0,1.0,1.0,2.0,0.5,1.0,1.0,1.0,1.0,1.0,0.5]],
[1.0, 200,9/100, [1.0,1.0,1.0,1.0,1.0,2.0,0.5,2.0,0.5,1.0,1.0,1.0,1.0,1.0,0.5]],
[0.9,  50,11/100,[1.0,1.0,1.0,1.0,0.5,1.0,2.0,2.0,0.5,1.0,1.0,1.0,1.0,1.0,0.5]],
[0.9, 100,25/100,[1.0,1.0,1.0,1.0,2.0,0.5,1.0,2.0,0.5,1.0,1.0,1.0,1.0,1.0,0.5]],
[1.1,  10, 5/100,[1.0,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,0.5,1.5,0.5]],
[1.1, 100,10/100,[1.0,1.0,1.0,1.0,1.0,1.0,1.0,2.0,1.0,0.5,1.0,2.0,1.0,1.0,2.0]],
[1.1,  30, 6/100,[1.0,1.0,1.0,1.0,1.0,1.0,1.0,2.0,2.0,1.0,1.0,0.5,1.0,1.0,2.0]],
[1.0, 100,10/100,[1.0,0.5,0.5,0.5,1.5,1.5,1.5,2.0,1.0,1.0,1.0,1.0,2.0,0.5,2.0]],
[1.0,  50,15/100,[1.0,1.0,1.0,1.0,1.0,1.0,1.0,2.0,0.5,2.0,1.0,1.0,1.0,1.0,2.0]],
[1.0, 150,15/100,[1.0,1.0,1.0,1.0,1.0,1.0,1.0,2.0,1.0,1.0,0.5,1.0,2.0,2.0,2.0]],
[1.0, 100,20/100,[1.0,1.5,1.5,1.5,0.5,0.5,0.5,2.0,1.0,1.0,2.0,1.0,0.5,1.0,2.0]],
[1.0, 100,10/100,[1.0,1.5,1.5,1.5,1.5,1.5,1.5,2.0,0.5,0.5,0.5,0.5,0.5,0.5,1.0]]
]
talentResisting=[ # 三才者,天地人,「才」译作talent
[1.0,1.1,0.9,1.0,1.0],
[0.9,1.0,1.1,1.0,1.0],
[1.1,0.9,1.0,1.0,1.0],
[1.0,1.0,1.0,1.0,1.1],
[1.0,1.0,1.0,1.1,1.0],
]
servantData={
#  0 class       1 rank     2 card   3 talent 4(houguType  houguColor) 5((skillType    skillTarget) ...)
#     0 Shielder   0 gold     1 3Q     0 sky    0 targeted 0 Arts         0 disable    0 ownAll         
#     1 Saber      1 silver   2 2Q2B   1 land   1 area     1 Quick        1 immediate  1 ownOne         
#     2 Archer     2 bronze   3 2Q2A   2 human  2 support  2 Buster       2 charge     2 ownExceptSelf  
#     3 Lancer                4 3B     3 star                             3 hougu      3 enemyAll       
#     4 Rider                 6 2A2B   4 beast                            4 color      4 enemyOne       
#     5 Caster                7 3A                                        5 atk        5 self           
#     6 Assassin                                                          6 critical   6 force-1        
#     7 Berserker     The following servants are not included             7 recovery   7 force-2        
#     8 Ruler           83 Solomon                                        8 dodge      8 force-3        
#     9 Avenger        149 Tiamat                                         9 stamina                     
#    10 Alterego       151 Goetia                                                                       
#    11 MoonCancer     152 Solomon                                                                      
#    12 Foreigner      168 BeastIII/R                                                                   
#    13 Pretender      240 BeastIII/L                                                                   
#    14 Beast          333 BeastIV                                                                      
1:(0,0,6,1,(2,0),((1,0),(2,1),(1,5))),
2:(1,0,6,1,(1,2),((5,0),(3,5),(2,5))),
3:(1,0,6,2,(1,2),((4,5),(2,5),(5,0))),
4:(1,0,6,1,(1,2),((2,5),(4,5),(1,0))),
5:(1,0,6,2,(1,0),((2,5),(7,5),(9,5))),
6:(1,0,6,1,(1,2),((2,5),(7,5),(4,5))),
7:(1,1,2,2,(0,1),((3,0),(5,0),(5,1))),
8:(1,0,6,2,(1,2),((3,0),(2,5),(5,5))),
9:(1,1,6,2,(2,0),((3,0),(1,5),(4,5))),
10:(1,0,6,2,(2,0),((8,5),(1,5),(7,5))),
11:(2,0,7,2,(1,2),((8,5),(6,5),(3,6))),
12:(2,0,6,0,(1,2),((5,0),(1,5),(2,5))),
13:(2,1,3,2,(0,0),((1,3),(1,5),(8,5))),
14:(2,0,3,1,(1,1),((4,0),(6,5),(8,5))),
15:(2,1,3,0,(0,0),((2,5),(1,4),(4,5))),
16:(2,2,6,1,(1,2),((1,5),(6,5),(2,5))),
17:(3,1,2,0,(0,1),((9,5),(8,5),(7,5))),
18:(3,0,2,2,(1,2),((5,2),(5,3),(9,5))),
19:(3,2,3,2,(2,0),((1,4),(1,5),(1,3))),
20:(3,1,2,0,(0,1),((6,5),(8,5),(6,5))),
21:(3,2,2,2,(2,2),((1,5),(9,5),(4,0))),
22:(3,1,2,3,(1,2),((2,5),(7,5),(9,1))),
23:(4,1,3,1,(1,1),((1,4),(5,5),(2,5))),
24:(4,2,3,2,(0,0),((1,5),(7,5),(9,5))),
25:(4,2,6,2,(1,2),((3,0),(9,5),(7,5))),
26:(4,1,3,2,(2,0),((6,0),(9,1),(4,0))),
27:(4,1,3,2,(0,1),((4,5),(5,5),(8,5))),
28:(4,1,3,2,(1,1),((5,0),(1,4),(4,0))),
29:(4,0,3,2,(1,1),((5,0),(1,5),(7,5))),
30:(4,0,7,2,(1,2),((7,5),(7,0),(5,4))),
31:(5,1,7,1,(0,0),((2,5),(7,5),(1,1))),
32:(5,1,7,2,(1,2),((1,5),(3,3),(1,3))),
33:(5,2,7,2,(2,0),((6,0),(2,5),(1,1))),
34:(5,2,7,2,(1,2),((4,0),(8,5),(6,1))),
35:(5,1,7,1,(1,2),((2,4),(1,5),(1,4))),
36:(5,2,7,3,(2,0),((4,0),(3,4),(6,0))),
37:(5,0,7,2,(2,0),((2,1),(2,0),(2,0))),
38:(5,1,7,0,(1,2),((2,5),(8,5),(2,5))),
39:(6,2,1,2,(0,1),((8,5),(6,5),(6,5))),
40:(6,2,1,2,(0,1),((6,5),(6,5),(8,5))),
41:(6,0,1,0,(2,2),((2,5),(1,4),(5,0))),
42:(6,1,1,2,(0,1),((6,5),(5,5),(4,5))),
43:(6,2,1,2,(0,2),((1,5),(7,1),(1,5))),
44:(6,2,1,1,(1,0),((1,5),(1,4),(1,5))),
45:(6,2,1,2,(2,0),((6,0),(5,3),(5,4))),
46:(6,0,1,1,(0,2),((2,5),(5,4),(1,5))),
47:(7,0,4,0,(0,2),((5,5),(8,5),(9,5))),
48:(7,0,4,1,(1,1),((6,5),(6,5),(6,5))),
49:(7,1,4,2,(0,2),((5,5),(1,5),(3,5))),
50:(7,2,4,2,(1,2),((1,5),(2,5),(4,5))),
51:(7,0,4,2,(0,2),((5,5),(2,5),(7,5))),
52:(7,0,6,1,(0,0),((2,5),(5,5),(9,5))),
53:(7,2,4,1,(2,0),((5,5),(1,5),(4,5))),
54:(7,2,4,2,(2,0),((5,5),(7,5),(4,5))),
55:(7,1,4,2,(1,2),((1,5),(7,5),(9,5))),
56:(7,1,4,1,(1,2),((1,5),(5,4),(4,5))),
57:(7,2,4,2,(1,2),((5,4),(9,5),(7,5))),
58:(7,0,4,1,(1,1),((5,5),(2,5),(7,5))),
59:(8,0,7,3,(2,0),((1,5),(3,4),(1,4))),
60:(2,0,3,0,(0,0),((5,5),(1,5),(8,5))),
61:(5,0,7,2,(1,2),((1,5),(4,5),(2,5))),
62:(5,0,7,0,(2,0),((2,2),(1,5),(4,1))),
63:(2,1,7,0,(0,2),((7,5),(8,0),(5,0))),
64:(3,1,2,2,(1,2),((3,0),(1,4),(7,5))),
65:(4,0,6,3,(1,2),((3,0),(4,5),(2,5))),
66:(4,0,3,2,(0,1),((9,5),(6,5),(5,5))),
67:(5,0,7,1,(2,0),((2,5),(7,0),(7,1))),
68:(1,0,2,2,(0,1),((4,5),(2,5),(8,5))),
69:(2,0,6,2,(1,2),((1,0),(1,5),(6,5))),
70:(3,0,2,3,(0,1),((8,5),(2,1),(1,5))),
71:(3,1,3,1,(0,1),((8,5),(1,3),(6,5))),
72:(1,1,4,1,(1,2),((5,5),(1,5),(8,5))),
73:(4,0,6,2,(1,2),((6,1),(6,0),(4,5))),
74:(5,0,7,2,(1,0),((6,5),(1,5),(2,5))),
75:(6,0,1,1,(0,1),((8,5),(6,4),(7,1))),
76:(1,0,6,1,(1,2),((4,5),(4,5),(2,5))),
77:(2,0,6,3,(1,2),((1,2),(9,5),(2,5))),
78:(3,0,2,0,(1,2),((2,5),(6,5),(5,0))),
79:(5,1,7,2,(1,0),((2,5),(4,0),(9,1))),
80:(5,1,6,2,(1,2),((6,5),(8,5),(3,5))),
81:(6,1,2,1,(2,2),((5,5),(1,5),(6,5))),
82:(7,0,4,1,(1,1),((1,5),(5,4),(3,5))),
84:(2,0,7,0,(1,2),((6,5),(1,5),(3,5))),
85:(3,0,2,0,(1,2),((1,4),(3,5),(2,5))),
86:(6,0,3,3,(0,1),((5,3),(8,5),(5,5))),
87:(3,0,3,0,(1,0),((6,0),(2,5),(4,5))),
88:(3,0,2,0,(0,2),((3,5),(2,5),(6,1))),
89:(7,0,4,1,(0,2),((3,5),(6,5),(9,5))),
90:(1,0,6,2,(0,0),((2,1),(5,1),(7,1))),
91:(1,0,6,2,(1,0),((4,5),(5,5),(7,5))),
92:(6,0,3,2,(0,0),((4,5),(8,5),(2,5))),
93:(8,0,6,2,(1,2),((1,1),(1,5),(4,5))),
94:(4,0,1,1,(1,1),((5,5),(1,4),(1,5))),
95:(2,1,6,0,(1,2),((5,0),(1,5),(1,5))),
96:(9,0,2,2,(1,1),((5,5),(1,5),(2,5))),
97:(7,0,6,2,(2,0),((7,1),(1,5),(4,1))),
98:(7,0,4,1,(0,2),((6,3),(8,5),(9,5))),
99:(4,0,6,1,(0,2),((1,5),(5,5),(5,4))),
100:(5,0,7,2,(1,0),((2,0),(1,5),(4,0))),
101:(1,0,6,0,(0,2),((6,5),(5,0),(9,5))),
102:(3,0,3,2,(0,0),((6,5),(8,5),(4,5))),
103:(5,0,7,2,(1,0),((1,1),(1,5),(3,1))),
104:(5,1,6,2,(1,0),((4,5),(4,5),(4,5))),
105:(2,1,3,2,(0,1),((6,5),(2,5),(8,5))),
106:(9,0,6,2,(0,2),((6,5),(5,0),(8,5))),
107:(9,3,3,2,(2,0),((6,4),(2,4),(1,5))),
108:(4,0,6,2,(1,2),((5,0),(3,0),(4,5))),
109:(6,0,3,2,(0,0),((4,5),(6,5),(6,1))),
110:(6,1,3,2,(0,0),((6,5),(8,5),(7,5))),
111:(5,0,7,0,(2,0),((7,5),(8,5),(7,1))),
112:(6,0,3,1,(1,0),((5,3),(3,5),(2,5))),
113:(5,0,7,2,(0,2),((2,5),(5,5),(6,0))),
114:(7,0,6,0,(1,2),((6,5),(8,5),(1,5))),
115:(4,0,2,1,(0,1),((4,5),(2,5),(7,5))),
116:(7,0,4,1,(0,2),((3,5),(2,1),(1,5))),
117:(6,1,1,2,(1,1),((6,3),(8,1),(5,3))),
118:(4,0,6,0,(0,2),((1,5),(7,5),(2,0))),
119:(3,0,2,0,(1,2),((4,5),(5,0),(2,5))),
120:(5,0,7,1,(1,0),((4,5),(2,5),(9,5))),
121:(1,0,6,1,(0,0),((2,5),(6,5),(1,5))),
122:(2,0,3,1,(0,1),((8,5),(2,5),(6,4))),
123:(1,0,4,1,(1,2),((4,5),(5,5),(2,5))),
124:(6,1,3,2,(0,0),((3,4),(6,4),(4,5))),
125:(2,1,6,2,(1,2),((4,5),(8,5),(7,0))),
126:(1,1,2,3,(0,2),((3,0),(2,5),(1,0))),
127:(5,0,7,3,(1,0),((9,5),(1,5),(2,5))),
128:(3,0,2,0,(0,2),((5,0),(5,4),(2,5))),
129:(2,0,3,1,(0,0),((4,5),(7,5),(5,0))),
130:(5,0,7,2,(1,0),((5,0),(1,5),(8,5))),
131:(2,0,6,2,(0,2),((5,0),(2,5),(9,5))),
132:(4,0,3,1,(1,0),((4,5),(8,5),(2,5))),
133:(6,0,1,3,(1,1),((6,5),(7,1),(4,5))),
134:(3,0,2,1,(0,2),((6,3),(4,5),(5,4))),
135:(8,0,4,2,(0,2),((2,5),(7,5),(1,5))),
136:(5,0,7,2,(0,2),((4,5),(2,5),(9,1))),
137:(2,0,3,0,(0,0),((8,5),(4,5),(2,5))),
138:(1,0,6,1,(0,2),((8,5),(4,5),(8,5))),
139:(6,0,2,2,(1,2),((7,5),(1,5),(8,5))),
140:(3,0,2,2,(0,2),((5,5),(3,0),(1,5))),
141:(3,0,2,2,(1,2),((6,1),(2,5),(8,5))),
142:(2,0,6,0,(1,2),((5,0),(2,5),(5,5))),
143:(3,0,1,0,(0,2),((4,5),(8,5),(7,5))),
144:(4,0,6,0,(0,2),((5,0),(9,1),(2,5))),
145:(5,0,7,2,(1,0),((6,0),(5,0),(4,0))),
146:(3,0,3,1,(0,1),((1,4),(5,5),(8,5))),
147:(9,0,6,1,(1,2),((4,5),(9,5),(1,4))),
148:(3,1,2,1,(0,2),((8,5),(5,5),(6,5))),
150:(5,0,7,1,(2,0),((2,0),(8,0),(4,1))),
153:(1,0,4,2,(0,2),((1,5),(4,5),(8,5))),
154:(6,0,4,2,(0,2),((2,5),(5,5),(4,5))),
155:(7,0,2,3,(0,1),((1,5),(4,5),(5,1))),
156:(2,0,7,2,(0,2),((6,5),(2,5),(5,2))),
157:(2,0,3,2,(0,0),((1,5),(4,5),(5,5))),
158:(9,0,3,1,(0,1),((6,5),(5,5),(1,4))),
159:(6,0,1,2,(0,1),((6,5),(4,5),(6,5))),
160:(1,0,6,1,(1,2),((4,5),(6,5),(2,5))),
161:(7,0,2,2,(0,2),((4,0),(9,5),(6,5))),
162:(7,0,4,2,(1,2),((1,5),(1,5),(1,4))),
163:(10,0,2,1,(0,1),((8,5),(5,5),(3,5))),
164:(10,0,4,1,(1,2),((1,5),(1,5),(5,5))),
165:(1,0,6,0,(1,2),((4,5),(1,4),(1,5))),
166:(11,0,3,2,(0,0),((7,1),(8,4),(6,5))),
167:(10,0,6,4,(1,0),((2,5),(5,3),(8,5))),
169:(5,0,7,2,(1,0),((2,5),(1,5),(9,5))),
170:(6,0,2,2,(0,1),((5,4),(2,5),(4,5))),
171:(7,0,4,1,(0,2),((5,0),(1,5),(4,5))),
172:(4,1,6,2,(1,2),((3,0),(2,5),(4,5))),
173:(8,0,3,3,(2,0),((6,4),(2,5),(8,5))),
174:(7,2,4,1,(1,2),((4,0),(7,0),(5,3))),
175:(5,0,6,2,(1,2),((2,5),(5,5),(9,1))),
176:(1,0,2,1,(0,1),((1,5),(1,5),(3,5))),
177:(6,0,3,0,(1,0),((1,5),(1,5),(3,5))),
178:(7,0,4,2,(0,2),((8,5),(1,5),(5,5))),
179:(4,0,3,2,(0,1),((4,5),(6,1),(4,5))),
180:(2,0,3,2,(1,0),((1,5),(1,5),(4,5))),
181:(3,0,2,0,(0,2),((6,5),(4,1),(5,0))),
182:(4,0,3,0,(1,1),((4,0),(8,5),(8,5))),
183:(3,0,2,0,(1,1),((4,5),(5,5),(7,1))),
184:(2,0,6,1,(0,2),((3,5),(6,5),(9,5))),
185:(6,0,3,1,(0,0),((1,4),(4,5),(2,5))),
186:(3,1,1,2,(2,0),((6,5),(4,5),(5,4))),
187:(1,0,6,2,(0,0),((4,5),(8,5),(1,5))),
188:(6,0,2,1,(1,2),((4,5),(8,1),(8,1))),
189:(6,0,3,1,(2,1),((6,5),(6,1),(5,4))),
190:(10,0,4,2,(0,2),((1,5),(2,5),(3,5))),
191:(10,0,4,2,(0,2),((1,5),(2,5),(3,5))),
192:(5,0,7,0,(0,2),((2,5),(5,3),(6,0))),
193:(3,0,2,0,(1,2),((4,5),(2,5),(6,5))),
194:(5,0,6,2,(0,0),((5,0),(6,5),(4,0))),
195:(12,0,7,1,(0,2),((1,5),(1,3),(1,4))),
196:(3,0,2,1,(1,2),((8,5),(2,5),(3,0))),
197:(2,0,3,3,(0,1),((2,1),(3,1),(6,5))),
198:(12,0,6,2,(1,0),((2,5),(4,5),(4,5))),
199:(6,0,7,1,(1,2),((2,5),(1,5),(4,3))),
200:(2,0,6,2,(0,2),((4,5),(6,5),(9,5))),
201:(5,0,7,2,(1,0),((4,5),(5,0),(2,5))),
202:(7,0,2,1,(0,1),((4,5),(4,0),(8,5))),
203:(5,1,7,2,(1,2),((4,5),(2,5),(8,5))),
204:(9,1,6,1,(1,0),((1,5),(4,5),(5,5))),
205:(4,0,6,2,(1,2),((2,5),(1,5),(8,5))),
206:(4,0,3,1,(1,1),((4,5),(8,5),(2,5))),
207:(2,0,3,0,(0,0),((8,5),(6,5),(4,1))),
208:(5,0,6,2,(1,0),((7,5),(4,5),(2,5))),
209:(10,0,2,2,(1,2),((4,5),(2,5),(8,5))),
210:(6,1,3,2,(0,0),((6,5),(8,5),(6,5))),
211:(4,0,6,2,(0,0),((5,0),(2,0),(4,0))),
212:(2,0,6,3,(1,2),((5,5),(3,0),(1,5))),
213:(1,0,6,1,(0,2),((6,5),(9,5),(6,1))),
214:(3,0,2,0,(1,1),((3,5),(8,5),(1,5))),
215:(5,0,3,0,(2,0),((4,1),(5,3),(2,1))),
216:(2,0,6,2,(1,0),((8,5),(2,5),(5,2))),
217:(3,0,2,1,(0,2),((3,5),(7,5),(6,5))),
218:(6,0,1,2,(1,1),((2,5),(8,5),(6,5))),
219:(7,0,4,2,(0,2),((1,5),(5,5),(2,5))),
220:(11,0,6,1,(1,2),((6,5),(2,5),(1,5))),
221:(1,0,6,1,(0,0),((1,5),(1,3),(5,2))),
222:(12,0,6,3,(0,0),((8,5),(6,5),(2,5))),
223:(1,0,2,1,(0,1),((8,5),(6,5),(1,5))),
224:(10,0,6,0,(0,0),((8,5),(4,5),(1,5))),
225:(5,0,7,1,(0,2),((6,4),(4,5),(5,5))),
226:(7,0,4,2,(1,1),((8,5),(4,5),(1,5))),
227:(1,0,6,2,(2,0),((8,5),(2,1),(4,0))),
228:(3,0,3,2,(2,0),((4,5),(6,5),(2,5))),
229:(8,0,6,2,(2,0),((5,3),(5,5),(2,5))),
230:(6,0,2,1,(1,2),((1,5),(1,5),(2,5))),
231:(4,1,3,1,(1,1),((4,5),(8,5),(5,5))),
232:(3,0,3,1,(1,1),((4,5),(9,5),(2,1))),
233:(8,0,2,0,(1,2),((1,5),(6,1),(4,5))),
234:(1,0,6,1,(0,0),((8,5),(5,3),(2,0))),
235:(6,0,6,2,(0,0),((6,5),(8,5),(5,5))),
236:(5,0,7,2,(2,0),((4,5),(9,5),(2,1))),
237:(5,0,3,2,(1,0),((5,0),(2,5),(1,0))),
238:(10,0,6,1,(1,2),((1,5),(0,0),(5,5))),
239:(6,0,2,0,(0,1),((3,1),(9,5),(2,5))),
241:(4,0,3,2,(2,0),((2,0),(2,1),(2,1))),
242:(8,0,6,0,(0,0),((5,1),(4,5),(2,5))),
243:(6,0,1,2,(1,2),((5,5),(8,5),(2,5))),
244:(11,0,7,0,(1,0),((1,0),(5,5),(8,1))),
245:(1,0,2,2,(1,1),((5,0),(1,1),(9,5))),
246:(2,1,6,2,(0,0),((6,4),(4,5),(6,5))),
247:(7,0,4,0,(1,2),((5,5),(2,5),(1,5))),
248:(2,0,2,0,(0,2),((2,5),(4,5),(4,5))),
249:(5,1,7,1,(2,0),((7,1),(1,0),(2,0))),
250:(9,0,4,1,(1,2),((1,5),(8,5),(1,5))),
251:(7,1,6,2,(0,2),((6,5),(5,5),(6,5))),
252:(3,0,6,2,(0,0),((4,5),(8,5),(5,0))),
253:(4,0,6,2,(1,0),((1,5),(8,5),(2,0))),
254:(1,2,6,1,(1,0),((7,1),(8,1),(2,2))),
255:(2,2,3,1,(0,1),((8,5),(5,5),(2,5))),
256:(3,2,2,1,(0,2),((9,5),(2,5),(1,5))),
257:(4,2,3,2,(1,1),((3,0),(6,5),(4,5))),
258:(5,2,7,2,(1,0),((6,1),(2,0),(4,1))),
259:(6,2,3,2,(0,0),((8,5),(5,5),(3,5))),
260:(7,2,6,1,(0,0),((5,5),(8,5),(1,5))),
261:(7,0,6,2,(1,0),((8,5),(3,5),(9,5))),
262:(2,0,7,1,(1,2),((8,5),(5,0),(4,5))),
263:(4,0,3,1,(1,1),((5,4),(2,5),(5,3))),
264:(1,0,3,2,(0,0),((2,5),(9,5),(4,5))),
265:(8,0,2,0,(1,2),((2,5),(4,1),(5,5))),
266:(3,0,3,1,(1,0),((4,5),(8,5),(5,5))),
267:(6,0,1,2,(1,1),((6,5),(8,5),(1,5))),
268:(9,0,6,3,(1,0),((5,0),(8,7),(2,5))),
269:(2,0,3,2,(0,1),((6,3),(2,5),(2,1))),
270:(1,0,3,1,(0,1),((1,5),(1,5),(4,5))),
271:(2,0,3,2,(1,1),((7,0),(9,1),(5,0))),
272:(2,0,4,1,(2,0),((4,5),(9,5),(6,5))),
273:(4,1,3,2,(0,0),((5,5),(5,5),(4,5))),
274:(4,0,6,0,(1,2),((8,5),(2,5),(5,3))),
275:(12,0,3,2,(0,0),((1,5),(2,3),(1,5))),
276:(2,0,3,2,(1,1),((1,0),(8,5),(2,5))),
277:(4,0,3,1,(1,0),((4,1),(2,5),(8,5))),
278:(1,0,3,0,(0,0),((6,5),(3,0),(8,5))),
279:(3,0,2,1,(1,2),((5,5),(1,5),(9,5))),
280:(3,0,6,0,(1,2),((5,0),(2,5),(4,5))),
281:(12,0,3,3,(1,1),((2,5),(8,5),(6,1))),
282:(7,0,4,1,(0,2),((6,5),(3,1),(7,0))),
283:(3,0,3,2,(1,0),((8,5),(6,5),(6,5))),
284:(5,0,7,3,(2,0),((2,0),(2,1),(8,1))),
285:(11,0,6,1,(1,0),((1,5),(2,5),(8,0))),
286:(2,0,3,2,(1,1),((4,5),(8,5),(1,5))),
287:(7,0,4,0,(1,2),((8,5),(1,5),(4,5))),
288:(3,0,2,1,(0,1),((9,5),(2,1),(4,5))),
289:(12,0,2,1,(1,2),((1,4),(1,3),(2,5))),
290:(1,0,6,1,(1,0),((9,5),(4,5),(1,5))),
291:(4,0,3,2,(0,0),((5,4),(1,4),(1,5))),
292:(8,0,6,1,(2,2),((1,0),(8,5),(2,5))),
293:(1,0,6,2,(0,0),((4,5),(8,5),(5,5))),
294:(2,2,2,2,(2,2),((1,4),(1,5),(7,5))),
295:(12,0,1,1,(2,0),((2,5),(1,0),(5,1))),
296:(4,0,6,0,(0,0),((3,0),(2,5),(4,0))),
297:(10,0,3,1,(1,1),((1,3),(9,5),(2,5))),
298:(1,0,6,2,(0,2),((4,5),(8,5),(4,5))),
299:(1,0,4,0,(1,2),((2,5),(4,5),(6,5))),
300:(3,0,3,0,(1,0),((4,5),(2,5),(1,5))),
301:(1,0,2,0,(0,1),((4,5),(8,5),(2,1))),
302:(1,0,6,2,(1,0),((4,5),(8,5),(2,5))),
303:(9,0,3,1,(0,1),((2,5),(9,5),(8,5))),
304:(6,0,2,1,(1,1),((8,5),(2,1),(5,0))),
305:(8,0,3,0,(1,1),((1,5),(2,5),(2,5))),
306:(7,0,4,1,(0,0),((2,5),(9,5),(1,5))),
307:(5,0,7,1,(2,0),((8,5),(2,5),(6,1))),
308:(12,0,2,3,(1,1),((8,5),(6,5),(5,0))),
309:(7,0,6,1,(1,2),((2,5),(2,1),(1,5))),
310:(1,0,4,1,(1,2),((4,5),(4,5),(1,5))),
311:(2,0,3,1,(0,1),((8,5),(2,5),(2,5))),
312:(3,0,6,1,(0,0),((2,5),(1,5),(2,5))),
313:(3,0,6,1,(1,0),((2,5),(1,5),(8,1))),
314:(6,0,2,4,(1,2),((2,1),(2,1),(4,1))),
315:(4,0,3,1,(1,0),((6,1),(2,5),(9,5))),
316:(13,0,2,1,(1,2),((2,0),(2,1),(0,1))),
317:(1,0,2,2,(1,1),((4,5),(2,5),(8,5))),
318:(2,0,3,2,(0,0),((2,5),(8,5),(3,5))),
319:(5,0,7,2,(0,0),((1,5),(1,5),(2,1))),
320:(8,0,6,2,(0,2),((4,1),(2,1),(3,0))),
321:(9,0,3,0,(1,0),((8,5),(3,5),(2,5))),
322:(4,0,6,1,(0,2),((5,0),(4,5),(1,5))),
323:(7,0,4,2,(0,1),((2,5),(8,5),(6,1))),
324:(12,0,2,1,(1,1),((2,5),(2,5),(1,5))),
325:(2,0,3,2,(1,0),((1,5),(9,5),(5,0))),
326:(4,0,6,2,(0,2),((8,5),(4,5),(2,5))),
327:(5,0,2,2,(0,1),((8,5),(5,5),(2,1))),
328:(9,0,6,3,(1,0),((6,1),(5,3),(2,5))),
329:(3,0,6,2,(1,0),((3,0),(2,5),(1,5))),
330:(5,0,3,2,(2,1),((2,1),(5,3),(2,1))),
331:(4,0,3,1,(1,1),((3,0),(1,5),(2,5))),
332:(4,0,6,1,(1,2),((1,5),(4,5),(2,5))),
334:(12,0,6,4,(1,2),((2,0),(3,1),(6,5))),
335:(13,0,6,1,(0,0),((4,5),(2,5),(1,5))),
336:(10,0,2,0,(2,1),((4,5),(2,5),(8,5))),
337:(1,0,6,2,(0,0),((4,0),(4,5),(2,5))),
338:(10,0,3,1,(1,0),((1,5),(9,1),(2,5))),
339:(10,0,4,1,(0,2),((4,5),(2,5),(4,0))),
340:(5,0,3,0,(1,1),((1,5),(1,5),(8,0))),
341:(3,2,6,2,(1,0),((4,0),(6,5),(2,0))),
342:(4,0,6,2,(2,2),((6,5),(4,0),(1,1))),
343:(1,0,3,3,(1,1),((8,1),(2,5),(4,5))),
344:(1,0,6,1,(0,2),((2,5),(4,5),(2,5))),
345:(7,0,6,1,(0,0),((5,3),(4,5),(2,1))),
346:(8,0,7,2,(1,0),((8,5),(4,5),(2,5))),
347:(3,0,2,1,(0,1),((9,5),(1,5),(2,5))),
348:(5,1,3,2,(1,1),((4,0),(6,1),(2,5))),
349:(4,0,3,2,(1,0),((2,5),(8,1),(4,5))),
350:(2,0,6,2,(1,2),((4,5),(2,5),(1,5))),
351:(11,0,6,3,(1,2),((5,5),(2,5),(2,5))),
352:(10,1,3,2,(2,0),((7,0),(4,0),(2,1))),
353:(13,0,7,1,(2,0),((4,1),(2,0),(1,5))),
354:(1,0,6,1,(1,2),((4,5),(1,1),(2,5))),
355:(7,0,6,0,(1,0),((5,0),(4,1),(1,5))),
356:(9,0,3,2,(0,0),((8,5),(2,5),(6,5))),
357:(8,0,2,0,(1,1),((4,1),(1,5),(2,1))),
358:(5,0,6,2,(1,2),((4,0),(2,0),(7,0))),
359:(6,0,3,0,(1,0),((4,5),(8,0),(2,1))),
360:(6,0,3,0,(1,0),((4,5),(8,0),(2,1))),
361:(6,0,3,0,(1,0),((4,5),(8,0),(2,1))),
362:(7,0,1,2,(1,1),((4,0),(2,1),(4,5))),
363:(1,0,3,2,(2,0),((5,0),(2,5),(8,0))),
364:(8,0,3,1,(1,0),((4,5),(2,5),(5,0))),
365:(6,0,2,2,(1,1),((4,5),(5,5),(2,5))),
366:(4,0,6,1,(0,2),((4,5),(1,5),(1,5))),
367:(13,0,2,2,(1,2),((3,5),(2,0),(4,5))),
368:(3,0,2,1,(1,1),((8,5),(1,5),(2,5))),
369:(10,0,3,1,(1,0),((5,1),(2,5),(9,5))),
370:(9,0,7,0,(1,0),((1,5),(2,5),(8,0))),
371:(6,0,6,0,(1,0),((9,0),(2,5),(9,5))),
372:(13,0,3,1,(1,1),((1,5),(9,0),(4,5))),
373:(12,0,4,3,(1,2),((5,5),(2,1),(8,5))),
374:(8,0,3,1,(1,0),((1,1),(2,5),(1,0))),
375:(2,0,2,2,(1,1),((3,0),(6,1),(2,5))),
376:(10,0,6,3,(1,2),((2,5),(4,5),(2,0))),
377:(14,0,4,4,(0,0),((1,5),(5,5),(1,5))),
378:(6,0,7,2,(0,0),((4,5),(9,5),(2,5))),
379:(1,0,3,1,(0,1),((5,5),(4,5),(8,5))),
380:(6,0,3,1,(1,1),((2,5),(2,5),(6,5))),
381:(3,0,2,0,(0,2),((2,5),(4,5),(5,5))),
382:(7,0,6,1,(1,0),((5,1),(4,5),(1,1))),
383:(2,0,3,0,(1,0),((2,5),(8,5),(3,5))),
384:(1,0,1,1,(0,1),((4,5),(2,5),(8,5))),
385:(5,0,6,1,(1,2),((1,5),(5,5),(2,0))),
386:(7,0,6,3,(0,0),((2,5),(2,1),(1,5))),
387:(4,0,3,0,(1,1),((3,0),(4,5),(2,1))),
388:(9,0,1,2,(0,1),((5,5),(9,1),(2,0))),
389:(12,0,7,1,(1,0),((1,5),(5,5),(4,5))),
390:(8,0,6,1,(1,0),((4,5),(1,5),(2,5))),
391:(2,0,3,1,(1,0),((1,5),(2,5),(3,5))),
392:(13,0,6,1,(1,2),((1,0),(1,5),(2,0))),
}
import cv2,tqdm
def readSplit(file,height):return(lambda img:[(lambda x:(x[...,:3],x[...,3]))(img[i*height:(i+1)*height])for i in range(img.shape[0]//height)])(cv2.imread(file,cv2.IMREAD_UNCHANGED))
servantImg={i:(
    readSplit(f'fgoImage/servant/{i}/card.png',47),
    readSplit(f'fgoImage/servant/{i}/portrait.png',63),
    None,# readSplit(f'fgoImage/servant/{i}/tachie.png',),
)for i in tqdm.tqdm(servantData,leave=False)}
