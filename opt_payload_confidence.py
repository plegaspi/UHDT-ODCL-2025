def opt_payload(targets, target_list):
    points = 400 
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
    
    ind = []
    if len(target_list) == 2:
        points= 200
        a=0
        while a<2:
            for i in range(4):
                if targets[i] == target_list[a][0]: 
                    payload[i] = 2
                    ind.append(i)

                else: 
                    pass 
            a+=1
        #check confidence and rearrange 
        # update confidence check by putting a restriction on how close the value can be to the bigger value
        if target_list[0][1] < target_list[1][1]:
            if target_list[0][1]<0.3 and target_list[0][1]<(target_list[1][1]- 0.1):
                if target_list[0][1]<0.2:
                  payload[ind[1]] = 4
                  payload[ind[0]] = 0
                else:
                    payload[ind[1]] = 3
                    payload[ind[0]] = 1

            else:
                pass
        else:
            if target_list[0][1] == target_list[1][1]:
                pass
            else:
                if target_list[1][1]<0.3 and target_list[1][1]<(target_list[0][1]- 0.1):
                    if target_list[1][1]<0.2:
                        payload[ind[0]] = 4
                        payload[ind[1]] = 0
                    else:
                        payload[ind[0]] = 3
                        payload[ind[1]] = 1
                else:
                    pass         
    
                  
        return payload, det_target
    else:
        pass
        
    
    # case 3 only 3 detections found
    if len(target_list) == 3:
        conf = []
        ind =[]
        a=0
        while a<3:
            for i in range(4):
                if targets[i] == target_list[a][0]:
                    payload[i] = 1
                    ind.append(i)
            else: 
                pass 
            a+=1
        for a in range(len(target_list)):
            conf.append(target_list[a][1])
        max_ = max(conf)
        for men in range(3):
            if max_ == target_list[men][1]:
                max_index = ind[men]
            else:
                pass

        rep =0 
        for n in range(len(target_list)):
            if max_ == target_list[n][1]:
                pass
            else:
                if rep == 1:
                    if target_list[n][1]<0.3 and target_list[n][1]< max_ - 0.15:
                        for man in range(4):
                            if targets[man]==target_list[n][0]:
                                payload[man] = 0
                                payload[max_index] = 4
                            else:
                                pass
                else:    
                    if target_list[n][1]<0.4 and target_list[n][1]<max_ - 0.15:
                        for man in range(4):
                            if targets[man]==target_list[n][0]:
                                payload[man] = 0
                                payload[max_index] = 3
                            else:
                                pass
                        rep = 1
                    else:
                        pass              
        return payload, det_target, max_index
    else:
        pass

    # case 4 4 detections found payload drop at each detection
    if len(target_list) == 4:
        a =0
        ind =[]
        while a<4:
            for i in range(4):
                if targets[i] == target_list[a][0]:
                        payload[i] = 1
                        ind.append(i)
                else: 
                    pass 
            a+=1
        
        conf = []
        for a in range(len(target_list)):
            conf.append(target_list[a][1])
        max_ = max(conf)
        for men in range(3):
            if max_ == target_list[men][1]:
                max_index = ind[men]
            else:
                pass

        rep =0 
        for n in range(len(target_list)):
            if max_ == target_list[n][1]:
                pass
            else:
                if rep ==0 :
                    if target_list[n][1]<0.45 and target_list[n][1]< max_ - 0.15:
                        for man in range(4):
                            if targets[man]==target_list[n][0]:
                                payload[man] = 0
                                payload[max_index] = 2
                                rep =1
                            else:
                                pass
                else:
                    if rep == 1:
                        if target_list[n][1]<0.30 and target_list[n][1]< max_ - 0.15:
                            for man in range(4):
                                if targets[man]==target_list[n][0]:
                                    payload[man] = 0
                                    payload[max_index] = 3
                                    rep =2
                                else:
                                    pass
                    else:
                        if rep == 2:
                            if target_list[n][1]<0.20 and target_list[n][1]< max_ - 0.15:
                                for man in range(4):
                                    if targets[man]==target_list[n][0]:
                                        payload[man] = 0
                                        payload[max_index] = 4
                                    else:
                                        pass
                            
                    

        
        return payload ,det_target
    
    # case 5 when more than 4 targets are detected
    if len(target_list)>4:
        conf = []
        for a in range(len(target_list)):
            conf.append(target_list[a][1])
        
        while len(target_list)>=5:
            min_index = conf.index(min(conf))
            target_list.pop(min_index)
            conf.pop(min_index)

        if len(target_list) == 4:
            a =0
            ind =[]
            while a<4:
                for i in range(4):
                    if targets[i] == target_list[a][0]:
                            payload[i] = 1
                            ind.append(i)
                    else: 
                        pass 
                a+=1
            
            conf = []
            for a in range(len(target_list)):
                conf.append(target_list[a][1])
            max_ = max(conf)
            for men in range(3):
                if max_ == target_list[men][1]:
                    max_index = ind[men]
                else:
                    pass

            rep =0 
            for n in range(len(target_list)):
                if max_ == target_list[n][1]:
                    pass
                else:
                    if rep ==0 :
                        if target_list[n][1]<0.45 and target_list[n][1]< max_ - 0.15:
                            for man in range(4):
                                if targets[man]==target_list[n][0]:
                                    payload[man] = 0
                                    payload[max_index] = 2
                                    rep =1
                                else:
                                    pass
                    else:
                        if rep == 1:
                            if target_list[n][1]<0.30 and target_list[n][1]< max_ - 0.15:
                                for man in range(4):
                                    if targets[man]==target_list[n][0]:
                                        payload[man] = 0
                                        payload[max_index] = 3
                                        rep =2
                                    else:
                                        pass
                        else:
                            if rep == 2:
                                if target_list[n][1]<0.20 and target_list[n][1]< max_ - 0.15:
                                    for man in range(4):
                                        if targets[man]==target_list[n][0]:
                                            payload[man] = 0
                                            payload[max_index] = 4
                                        else:
                                            pass
            return payload, det_target

if __name__ == "__main__":
    targets = ['bus', 'airplane', 'umbrella', 'car']
    # test for case_1
    target_list_0 = [['bus',0.4]]
    payload_0 , det_target_0 = opt_payload(targets, target_list_0)
    #print(payload_0, det_target_0)

    # test for case 2 
    target_list = [['car', 0.31], ['bus', 0.19]]
    payload,det_target= opt_payload(targets, target_list)
    #print(payload, det_target)

    #test for case 3 
    target_list_1 = [['bus', 0.3], ['car', 0.8], ['umbrella', 0.35]]
    payload_1 , det_target_1, index= opt_payload(targets, target_list_1)
    #print(payload_1, det_target_1, index)

    # test for case 4
    target_list_2 = [['bus', 0.28], ['car', 0.8], ['airplane', 0.43], ['umbrella',0.78]]
    payload_2, det_target_2= opt_payload(targets, target_list_2)
    #print(payload_2,det_target_2)

    #test case 5
    target_list_3 = [['bus', 0.5], ['car', 0.8], ['airplane', 0.6], ['umbrella',0.78], ['bus', 0.1], ['umbrella', 0.23]]
    payload_3 = opt_payload(targets, target_list_3)
    print(payload_3)


# confidence values be implemented using arbitrary values picked and another way would be weighing the values and using points to determine the most efficent way?
# general coordinates will be given for later










