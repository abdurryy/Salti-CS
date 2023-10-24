from salti import Salti

salti = Salti()
salti.on()

print(salti.call(input("Target: ")))

salti.hangup()
