class Patient:
    def __init__(self, name, age, district, gender):
        self.name = name
        self.age = age
        self.gender = gender
        self.district = district
patient_01 = Patient("John Doe", 30, "Kampala", "Male")
patient_02 = Patient("Jane Doe", 65, "Entebbe","Female")
print(f"{patient_01.name} is a {patient_01.age} {patient_01.gender} year old living in {patient_01.district}")
if patient_02.age > 60:
    print("High Risk")
else:    
    print("Low Risk")
    
    
    
Districts = ["Kampala", "Entebbe", "Jinja", "Gulu", "Mbale"]
for district in Districts:
#for district in Districts[1:3]:
    print(district)