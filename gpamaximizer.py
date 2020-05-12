import inflect

grades_dict = {"A+":4.3, "A":4.0, "A-":3.7, "B+":3.3, "B":3.0, "B-":2.7, "C+":2.3, "C":2.0, "C-":1.7, "D+":1.3, "D":1.0, "F":0.0}

def check_grade_input(grade):
    if grade[0] not in ["A", "B", "C", "D", "E","F","U","P"]:
        return False
    if len(grade) > 1:
        if grade[-1] not in ["-", "+"]:
            return False
    return True

# cgpa = float(input("what is your current TOTAL GRADE POINTS? (Including this sem)"))
# num_of_cmod = float(input("How many graded mods have you taken? (Including this sem)"))

output = ""

# number of mods this sem
num_of_mod = int(input("How many graded mods are you taking this sem?: "))

p = inflect.engine()
this_sem = []

for i in range (1, num_of_mod + 1):
    print("For the " + p.ordinal(i) + " mod,")
    print("How many credit unit (CU) is the module?:")
    cu = float(input())

    while cu % 0.5 != 0 & cu >= 0.5:
        print("Invalid CU")
        print("How many credit unit (CU) is the module?:")
        cu = float(input())

    print("What is the grade achieved?")
    grade = str(input())

    while not(check_grade_input(grade.upper())):
        print("Invalid Grade")
        print("What is the grade achieved?")
        grade = str(input())

    this_sem.append([cu, grade.upper()])

print(this_sem)