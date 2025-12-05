import os

file_names = []
folder_path = "Deck"

if os.path.exists(folder_path) and os.path.isdir(folder_path):
    for entry in os.listdir(folder_path):
        full_path = os.path.join(folder_path, entry)
        if os.path.isfile(full_path):
            file_names.append(entry)

if file_names:
    count = 1
    for filename in file_names:
        print("    " + str(count) + ': "' + filename + '",')
        count+=1

