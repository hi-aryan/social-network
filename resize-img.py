from PIL import Image

# open the specific avatar
img = Image.open('flasknetwork/static/img/happymonkey1.png')
# scale to max 125×125
img.thumbnail((125, 125))
# save into your “small” folder
img.save('flasknetwork/static/img/happymonkey2.png')