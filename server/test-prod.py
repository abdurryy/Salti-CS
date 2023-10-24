from salti import Salti

salti = Salti()
salti.hangup()
salti.off()
salti.on()

print(salti.call(input("Target: ")))

salti.hangup()
