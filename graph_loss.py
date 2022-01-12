import matplotlib.pyplot as plt
l = [1.1430052749389366, 0.006668427888546283, 0.012381236864236825, 0.0062358151739864325, 0.005334275914379982, 0.005045964566936819, 0.004548341604928666, 0.00523396465388626, 0.004903144036542558, 0.0042331320643295735, 0.0037410825882670104, 0.0036531402070136233, 0.003019838706191412, 0.002438410913937568, 0.0031661098677044546, 0.0021423447139221523, 0.0022080583048818946, 0.0019935358035969753, 0.0017172864539892728, 0.001712848574655206, 0.001487760095655495, 0.0015418382182666166, 0.0012956759817354428, 0.0012721018696374201, 0.0013226736973513007, 0.0010518998704064817, 0.0010393734327142818, 0.0010409617474838944, 0.000972753262705005, 0.0009484027099101179, 0.0009466223269148192, 0.0009268564256850262, 0.0008547394230431663, 0.0008667676258341803, 0.0007892442354098414, 0.0007770013565378727, 0.0007453067439079086, 0.0007606777977310218, 0.0007146654287463182, 0.0006967656779985565, 0.0007569087488290627, 0.0007845974498187008, 0.0007166957623153135, 0.0007005713155263273, 0.0006983042929617402, 0.0006720399342873158, 0.0006222324491838946, 0.0006398430655692865, 0.0006283136206506403, 0.0006248977046970527, 0.0005904364690073002, 0.0005749730049229958, 0.0005721727865650544, 0.0005747654059759454, 0.0005716168343256081, 0.000580311562493523, 0.0005492648912975584, 0.0005555885097535051, 0.0005454624943582104, 0.00054101493803935, 0.0005506307978051546, 0.0005313818199315946, 0.0005292898981273177, 0.000542928547574379, 0.000531938438594996, 0.0005217523401519682, 0.0005076934143982856, 0.0005124509795187675, 0.0005037006272763716, 0.0005209844204508461, 0.0004971909489396658, 0.0005038135175857419, 0.000498367077449476, 0.0004841366519797553, 0.0004893878888921356, 0.0004968367936655726, 0.0004944747406748083, 0.0004912880245558788, 0.00048466612928574457, 0.0004985035454872207, 0.0004897640755434571, 0.00048040914995255927, 0.0004864748975747005, 0.0004814793731199734, 0.0005031812281104586, 0.0004790031014118576, 0.0004954207607249688, 0.000494139431279169, 0.00047759139692045584, 0.00047742989631781595, 0.0004885852103281768, 0.0004903965759408435, 0.000495348080571444, 0.0004913397099597792, 0.00048646414976528154, 0.00048468960661018944, 0.00048494153073615936, 0.00047680793748987294, 0.00047099284048044104, 0.00046473593459062015, 0.0004769888401827841]
plt.figure()

plt.plot(l[1:])
plt.xlim([2,101])
plt.title('Loss over training episodes 2 to 100')
plt.xlabel('Episode')
plt.ylabel('Average Loss')
plt.savefig('loss_better.png')
plt.show()

plt.plot(l)
plt.title('Loss over training episodes')
plt.xlabel('Episode')
plt.ylabel('Average Loss')
plt.savefig('loss_full.png')
plt.show()
