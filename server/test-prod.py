from salti import Salti

salti = Salti()
salti.on()
salti.hangup()

print(salti.call(input("Target: ")))

salti.hangup()
