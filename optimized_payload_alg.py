
def opt_payload(targets, target_list):
    
    det_target =[]
    # getting target name only 
    for d in range(len(target_list)):
        det_target.append(target_list[d])

    payload = [0,0,0,0]
    #case 1 only 1 detection found 
    # drop all payloads onto detected target 
    if len(target_list)== 1:
        for i in range(4):
            if targets[i] == target_list[0][0]:
                payload[i] = 4
            else: 
                #no right detections drop payload at any target
                pass
        return  payload, det_target
    
    # case 2 only 2 detections found 
    if len(target_list) == 2:
        a=0
        while a<2:
            for i in range(4):
                if targets[i] == target_list[a][0]:
                    payload[i] = 2
                else: 
                    #no right detections drop payload at any target
                    pass 
            a+=1
        return payload,det_target
    else:
        pass
    
    # case 3 only 3 detections found
    if len(target_list) == 3:
        a=0
        while a<3:
            for i in range(4):
                if targets[i] == target_list[a][0]:
                    payload[i] = 1
            else: 
                #no right detections drop payload at any target
                pass 
            a+=1
        return payload, det_target
    else:
        pass

    # case 4 4 detections found payload drop at each detection
    if len(target_list) == 4:
        a =0
        while a<4:
            for i in range(4):
                if targets[i] == target_list[a][0]:
                    if payload == 0:
                        payload[i] = 1
                    else:
                        pass

                else: 
                    pass 
                #no right detections drop payload at any target
                pass 
            a+=1
        return payload ,det_target


if __name__ == "__main__":
    targets = ['bus', 'airplane', 'umbrella', 'car']
    target_list = [['umbrella', 0.5], ['car', 0.8]]
    payload , det_target= opt_payload(targets, target_list)
    print(payload, det_target)
    

# determine how we want to distribute the payloads for case 2 and 3
#  find out about misclassifications
# find about confidence values
# general coordinates will be given that are not



























'''
matched_target_list = []

safe_keep =[]
for i in range(len(target_ratio_list)):
    safe_keep.append(target_ratio_list[i])

# make a list of the possible objects
while len(target_ratio_list)>0:

    pred_1 = [target_ratio_list[0][1], target_classes[0]]
    pred_2 = [target_ratio_list[0][2], target_classes[1]]
    pred_3 = [target_ratio_list[0][3], target_classes[2]]
    pred_4= [target_ratio_list[0][4], target_classes[3]]
   
    matched_target = pred_1
    #compare with each object and find the highest ratio number

    if matched_target[0] < pred_1[0]:
        matched_target =pred_1
    else: 
        pass
    if matched_target[0] < pred_2[0]:
        matched_target =pred_2
    else:
         pass
    if matched_target[0] < pred_3[0]:
        matched_target =pred_3
    else:
         pass
 
    if matched_target[0] < pred_4[0]:
        matched_target = pred_4
    else:
         pass

    
    #put in list of correctly matched targets
    matched_target_list.append(matched_target)
    #remove the target and go to the next one
    target_ratio_list.pop(0)

# calculate the efficient amount of points to get from competition total 400 
# break it up into each scenario of detected payloads


#if only 1 detected payload drop all payloads 
if len(target_ratio_list) ==1:
    num_payloads = 4
    target_drop = matched_target_list[0]
else:
    pass

# if 4 detected payload 
if len(matched_target_list) == 4:
    # if there were multiple detected of the same target 
    mult = 0
    same_target = []
    conf_val = []
    index = []
    for a in range(4):
        check_target = matched_target_list[a][1] 
        for i in range(4):
            if i == a:
                pass
            else:
                if check_target == matched_target_list[i][1]:
                    mult += 1
                    same_target.append(safe_keep[a])
                    conf_val.append(matched_target_list[a][0])
                    index.append(a)
                    break
                else:
                    pass
    if mult>1:
        #compare confidence scores to see which one is higher 
        for c in range(len(conf_val)):
            if c ==0:
                highest = conf_val[0]
            else:
                if highest<conf_val[c] :
                    highest= conf_val[c]
                    max_ind =c
                    
                else:
                    pass
        # remove confidence value from input list and general targets
        target_classes.pop(safe_keep[0].index(conf_val[0])-1)
        for k in range(len(safe_keep)):
            safe_keep[k].remove(conf_val[k])
        
        # repeat process from the beginning
        matched_target_list =[]
        while len(safe_keep)>0:

            pred_1 = [safe_keep[0][1], target_classes[0]]
            pred_2 = [safe_keep[0][2], target_classes[1]]
            pred_3 = [safe_keep[0][3], target_classes[2]]
        
            matched_target = pred_1
            #compare with each object and find the highest ratio number

            if matched_target[0] < pred_1[0]:
                matched_target =pred_1
            else: 
                pass
            if matched_target[0] < pred_2[0]:
                matched_target =pred_2
            else:
                pass
            if matched_target[0] < pred_3[0]:
                matched_target =pred_3
            else:
                pass
            #put in list of correctly matched targets
            matched_target_list.append(matched_target)
            #remove the target and go to the next one
            safe_keep.pop(0)
            
    else:
        #all payloads match output [1, 1, 1, 1]
        pass
else:
    pass


'''