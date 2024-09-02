from classes import Target, Payload

def compare(payload, target):
    error1 = ["RED", "ORANGE"]
    arr1 = ['I', 'L']
    arr4 = ['M', 'E', 'K', 'H', '3']
    arr6 = ['9']
    arrC = ['U']
    arrG = ['C']
    arrJ = ['1', 'U', 'L']
    arrK = ['V']
    arrN = ['Z']
    arrM = ['W', 'N']
    arrO = ['0']
    arrQ = ['D', '0']
    arrS = ['5']
    arrT = ['1']
    arrV = ['U']
    arrZ = ['N']

    score = 0;
    if payload.shape == target.shape:
        score += 1
    
    if payload.shapeColor == target.shapeColor:
        score += 1

    # START color error checks
    elif any(target.shapeColor == match for match in error1) and any(payload.shapeColor == match for match in error1):
        score += 0.5
    elif target.shapeColor == target.alphanumColor:
        score += 0.5
    else:
        # START shape and alphnum color swap check
        if payload.shapeColor == target.alphanumColor or payload.alphanumColor == target.shapeColor:
            score += 0.5
        elif any(target.shapeColor == match for match in error1) and any(payload.alphanumColor == match for match in error1):
            score += 0.5
        # END shape and alphnum color swap check

    if payload.alphanumColor == target.alphanumColor:
        score += 1
    elif any(target.alphanumColor == match for match in error1) and any(payload.alphanumColor == match for match in error1):
        score += 0.5
    elif target.shapeColor == target.alphanumColor:
        score += 0.5
    else:
        # START shape and alphnum color swap check
        if payload.shapeColor == target.alphanumColor or payload.alphanumColor == target.shapeColor:
            score += 0.5
        elif any(target.alphanumColor == match for match in error1) and any(payload.shapeColor == match for match in error1):
            score += 0.5
        # END shape and alphnum color swap check

    #  END color error checks

    if payload.alphanum == target.alphanum:
        score += 1

    # START alphnum error checks
    elif any(char == payload.alphanum for char in target.alphanum):
        score += 0.5
    elif payload.alphanum == '1' and any(char in arr1 for char in target.alphanum):
        score += 0.5
    elif payload.alphanum == '4' and any(char in arr4 for char in target.alphanum):
        score += 0.5
    elif payload.alphanum == '6' and any(char in arr6 for char in target.alphanum):
        score += 0.5
    elif payload.alphanum == 'C' and any(char in arrC for char in target.alphanum):
        score += 0.5
    elif payload.alphanum == 'G' and any(char in arrG for char in target.alphanum):
        score += 0.5
    elif payload.alphanum == 'J' and any(char in arrJ for char in target.alphanum):
        score += 0.5
    elif payload.alphanum == 'K' and any(char in arrK for char in target.alphanum):
        score += 0.5
    elif payload.alphanum == 'N' and any(char in arrN for char in target.alphanum):
        score += 0.5
    elif payload.alphanum == 'M' and any(char in arrM for char in target.alphanum):
        score += 0.5
    elif payload.alphanum == 'O' and any(char in arrO for char in target.alphanum):
        score += 0.5
    elif payload.alphanum == 'Q' and any(char in arrQ for char in target.alphanum):
        score += 0.5
    elif payload.alphanum == 'S' and any(char in arrS for char in target.alphanum):
        score += 0.5
    elif payload.alphanum == 'T' and any(char in arrT for char in target.alphanum):
        score += 0.5
    elif payload.alphanum == 'V' and any(char in arrV for char in target.alphanum):
        score += 0.5
    elif payload.alphanum == 'Z' and any(char in arrZ for char in target.alphanum):
        score += 0.5
    # END alphnum color checks

    return score

#This function matches the payloads to the given targets.
def order_payloads(payloads0, targets0):
    payloads = payloads0
    targets = targets0
    payload_order = []
    target_scores = []
    hasConflicts = False
    unassigned_targets = []
    unassigned_payloads = [0, 1, 2, 3] #removed 4 (or 5th element) for testing purposes.
    ordered_payloads = []

    #In case there are missing targets, add dummy targets
    insert_index = 0
    latitude_array = [38.3143415, 38.3144689, 38.3144341, 38.3143899]
    longitude_array = [-76.5441875, -76.5449238, -76.5447173, -76.5444343]
    while (len(targets)<len(payloads)):
        targets.append(Target(latitude=latitude_array[insert_index], longitude=longitude_array[insert_index]))
        insert_index += 1
    

    #For each target, compare to all the payloads, generate a similarity score for each payload
    for target in targets:
        payload_scores = []
        for payload in payloads:
            payload_score = compare(payload, target)
            payload_scores.append(payload_score)
        #print("payload scores: ", payload_scores)
        target_scores.append(payload_scores)
#Take the highest payload score's index for each target
    #print("target scores: ", target_scores)
    for payload_scores in target_scores:
        #print("payload scores being checked:", payload_scores)
        payload_order.append(payload_scores.index(max(payload_scores)))
        #print("payload order:", payload_order)
    for index in payload_order:
        if payload_order.count(index) > 1: hasConflicts = True

    if hasConflicts:
        for i in range(len(payload_order)):
            if payload_order.count(payload_order[i]) != 1:
                unassigned_targets.append(i)
            if payload_order.count(payload_order[i]) == 1:
                unassigned_payloads.remove(payload_order[i])
            for j in range(len(unassigned_targets)):
                payload_order[unassigned_targets[j]] = unassigned_payloads[j]
        for payload_index in payload_order:
            #print(f'Dock: {payloads[payload_index].dock}, Shape:{payloads[payload_index].shape}, Shape Color: {payloads[payload_index].shapeColor}, Alphnum Color: {payloads[payload_index].alphanumColor}, Alphnum: {payloads[payload_index].alphanum}')
            ordered_payloads.append(payloads[payload_index])
    else:
        for payload_index in payload_order:
            #print(f'Dock: {payloads[payload_index].dock}, Shape:{payloads[payload_index].shape}, Shape Color: {payloads[payload_index].shapeColor}, Alphnum Color: {payloads[payload_index].alphanumColor}, Alphnum: {payloads[payload_index].alphanum}')
            ordered_payloads.append(payloads[payload_index])
    return ordered_payloads

    # note: ordered_payloads returns the payloads ordered in the order of the targets.
    # In other words, if the targets come in the order of 3 1 2 4, a "correct" ordered_payloads would hold payload 3, payload 1, payload 2, payload 4.
