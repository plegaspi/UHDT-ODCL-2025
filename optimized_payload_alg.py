# create a optimized payload matching algortihm 

# take the provided classes (this will be random? also not sure how it will be given
target_classes = ["sports_ball", "bus", "mattress", "motorcycle"]

# taking in a list of objects and number of how accurate it matches with every object need to correctly identify them
# not sure how data will be given just making it simple
target_ratio_list = [['target1',0.8,0.7,0.6, 0.4,], ['target2',0.9,0.4,0.5,0.7], ["target3",0.6,0.2,0.3,0.2], ["target4", 0.7,0.2,0.23,0.45]]
# target_ratio_list = [['target1',0.8,0.7,0.6, 0.4,]]
# targets 
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
      
        
    else:
        #all payloads match ?
        payload_target_1 = matched_target_list[0][1]
        num_1 = 1
        payload_target_2 = matched_target_list[1][1]
        num_2 = 1
        payload_target_3 = matched_target_list[2][1]
        num_3 = 1
        payload_target_4 = matched_target_list[3][1]
        num_4 = 1
else:
    pass

#print(same_target)
#print(safe_keep)
