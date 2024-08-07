from WDC import WDC
cl = WDC('/home/dell/Загрузки/rtae.png')
cl.read_img()
x, y = cl.extract_coordinates(1) # AE
cl.intepolate_by_coords(x, y, 1)
minutes, values = cl.get_values(1)
cl.make_plot(1)

