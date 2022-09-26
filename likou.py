# 最长公共前缀

class Solution(object):
    def longestCommonPrefix(self, strs):
        sig = True
        i = 0 
        if(strs==[]): # 判断是否为空
            return ""
        if(len(strs)==1):
            return strs[0] # 判断是否只有一个值
        if("" in strs): # 判断有没有空值
            return ""
        while(sig == True):
            if(len(strs[0])<=i):
                return strs[0][0:i]
            temp = strs[0][i]
            for j in strs[1:]:
                if(temp!= j[i]):
                    return strs[0] [0:i]
                elif(temp==j[i] and len(j)==i+1): 
                    sig = False
                    k = i
            i += 1
        return strs[0][0:k+1]
if __name__=="__main__":
    s = Solution()
    li = ["flower","flo","flight"]
    print(s.longestCommonPrefix(li))