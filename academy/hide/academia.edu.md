

    from __future__ import division, print_function


    str(75)




    '75'




    def bottles_kegs(num):
        '''
        '''
        kegs = False
        bottles = False
        
        kegs = (num % 5) == 0
        bottles = (num % 7) == 0
        
        string_num = str(num)
        if str(7) in string_num:
            bottles = True
        if str(5) in string_num:
            kegs = True
        if bottles and kegs:
            print("Bottles and Kegs")
        elif bottles:
            print("Bottles")
        elif kegs:
            print("Kegs")
        else:
            print(num)


    bottles_kegs(4)

    4



    bottles_kegs(75)

    Bottles and Kegs



    bottles_kegs(15)

    Kegs



    bottles_kegs(17)

    Bottles



    def div5(num):
        '''
        Returns True when num is divisible by 5
        '''
        return num % 5 == 0
    
    def div7(num):
        return num % 7 == 0
    
    def has5(num):
        return str(5) in str(num)
    
    def has7(num):
        return str(7) in str(num)
        


    def get_tests():
        test_encode = []
        test_set = set([])
        test_nums = []
        for i in range(100000):
            count = [0,0,0,0]
            if div5(i):
                count[0]=1
            if div7(i):
                count[1]=1
            if has5(i):
                count[2]=1
            if has7(i):
                count[3]=1
            count = tuple(count)
            if count not in test_set:
                test_set.add(count)
                test_nums.append(i)
    
        return test_nums
            


    get_tests()




    [0, 1, 5, 7, 10, 14, 17, 35, 51, 56, 57, 70, 75, 170, 175, 357]




    0 % 5




    0




    
