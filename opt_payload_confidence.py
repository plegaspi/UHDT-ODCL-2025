from classes import Target

def opt_payload(targets, targ):
    #formatting input
    conf =[]
    for a in range(len(targ)):
        conf.append(targ[a].confidence_scores)
    dum = []
    while (len(targ)+len(dum))<4:
        dummy = Target("Dummy", 0.0, latitude=21.3 + len(conf)*0.01, longitude=-157.8 - len(conf)*0.01)
        dum.append(dummy)

# 30 points unique target , 50 within 25 feet of any target, 20 points lands
    maxx = max(conf)
    max_ind = conf.index(maxx)
    #case 1 only 1 detection found 
    if len(conf)== 1:
        if maxx>=0.5:
            targ[0].num_payloads = 4
        else:
            targ[0].num_payloads = 3
            dum[0].num_payloads = 1
            targ.append(dum[0]) 
            if maxx<0.3:
                targ[0].num_payloads = 2
                dum[1].num_payloads = 1
                targ.append(dum[1])
                if maxx<=0.2:
                    targ[0].num_payloads = 1
                    dum[2].num_payloads =1
                    targ.append(dum[2])

    # case 2 only 2 detections found 
    if len(conf)==2:
        a=0 
        for i in range(len(conf)):
            if conf[i]>=0.3:
                targ[i].num_payloads = 2
            else:
                if a == 0:
                    targ[i].num_payloads = 1
                    dum[0].num_payloads =1 
                    targ.append(dum[0])
                else:
                    targ[i].num_payloads = 1
                    dum[1].num_payloads = 1 
                    targ.append(dum[1])          
              
    # case 3 only 3 detections found
    if len(conf) == 3:
        targ[max_ind].num_payloads = 2
        for i in range(len(conf)):
            if max_ind == i:
                if conf[i]>=0.3:
                    pass
                else:
                    targ[max_ind].num_payloads = 1
                    dum[0].num_payloads =1
                    targ.append(dum[0])
            else:
                targ[i].num_payloads = 1

    
    # case 4/5 when more than 4 targets are detected
    if len(conf)>=4:    
        while len(conf)>=5:
            min_index = conf.index(min(conf))
            for i in range(len(conf)):
                targ[i].pop(min_index)
                conf.pop(min_index)
        for i in range(len(conf)):
            if conf[i]>=0.1:
               targ[i].num_payloads =1 
            else:
                targ[max_ind] += 1 

    #change value of num_payloads in target class functionn 
    return targ
    
def print_test_results(title, results):
    print(f"\n=== {title} ===")
    for t in range(len(results)):
        print(f"{results[t].predicted_classes:12} | Conf: {results[t].confidence_scores:.2f} | Payloads: {results[t].num_payloads}")

if __name__ == "__main__":
    targets = ['bus', 'airplane', 'umbrella', 'car']

    #Test case 1: detection, high confidence
    t1 = Target("car", 0.2, 34.0, -118.2)
    test_1_high = [t1]
    result_1_high = opt_payload(targets, test_1_high)
    print_test_results("Case 1 - One Detection (Low Confidence)", result_1_high)
   
    # TEST CASE: 4 detections, scoring-based fallback
    t10 = Target("bus", 0.6, 35.1, -120.3)
    t11 = Target("car", 0.55, 34.2, -118.5)
    t12 = Target("airplane", 0.65, 36.4, -121.7)
    t13 = Target("umbrella", 0.62, 37.0, -122.1)
    test_4 = [t10, t11, t12, t13]
    result_4 = opt_payload(targets, test_4)
    print_test_results("Case 4 - Four Detections", result_4)

    t7 = Target("umbrella", 0.72, 47.6, -122.3)
    t8 = Target("bus", 0.65, 35.2, -120.5)
    t9 = Target("car", 0.25, 33.9, -117.8)
    test_3_mixed = [t7, t8, t9]
    result_3_mixed = opt_payload(targets, test_3_mixed)
    print_test_results("Case 3 - Three Detections (Mixed Confidence)", result_3_mixed)










