
def describe_patient(name, age, district):
    print(f"{name} is a {age} year old living in {district}")
describe_patient("John Doe", 30, "Kampala")

def is_elderly(age):
    
    if age >= 60:
        return True
    else:
        return False
    
one_patient = {"name": "John Doe", "age": 30, "district": "Kampala", "condition": "Healthy"}
for key, value in one_patient.items():
    print(f"{value}" )   