from matplotlib import pyplot as plt


#plt.figure() #figsize=(3,2)
"""
ax1 = plt.subplot(1,3,1)
ax2 = plt.subplot(2,2,4)
ax3 = plt.subplot(2,2,5)
ax4 = plt.subplot(3,2,6)
#ax1 = plt.subplot(2,3,1)
#ax2 = plt.subplot(2,3,2)
#ax3 = plt.subplot(2,3,3)
#ax4 = plt.subplot(2,1,2)

axes = [ax1, ax2, ax3, ax4]
"""

plt.figure(figsize=(16,8))
# Left column
plt.subplot(3, 2, (1, 5))

# Right column
plt.subplot(3, 2, 2)
plt.subplot(3, 2, 4)
plt.subplot(3, 2, 6)



"""
plt.subplot(3,2,1)
plt.subplot(3,2,3)
plt.subplot(3,2,5)
plt.subplot(1,2,2)
"""

#plt.subplot(2,2,4)
plt.show()