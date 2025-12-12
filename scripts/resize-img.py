from PIL import Image

# open the specific avatar
img = Image.open('flasknetwork/static/profile_pics/default4.png')
# scale to max 125×125
img.thumbnail((125, 125))
# save into your “small” folder
img.save('flasknetwork/static/profile_pics/default4_small.png')