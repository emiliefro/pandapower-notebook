import pandas as pd
import pandapower as pp
import numpy as np
import pandapower.networks as networks

# https://pandapower.readthedocs.io/en/v2.9.0/networks/example.html
networks.simple_mv_open_ring_net()


def compute_reactive_power(p_mw, cos_phi=0.97,):
    """Calculates reactive power according to given active power and
    power factor
    """
    return p_mw * np.tan(np.arccos(cos_phi))


def create_net():
    csv = pd.read_csv('pv.csv', delimiter=';',
                      parse_dates=[0],
                      encoding="utf-8-sig")
    dates = csv["Datum"].tolist()
    power = csv["MW"].tolist()

    net = pp.create_empty_network()

    bus_hv = pp.create_bus(net, name="110 kV bar", vn_kv=110, type='b',
                           geodata=[0, 0])
    bus_mv = pp.create_bus(net, name="20 kV bar", vn_kv=20, type='b',
                           geodata=[0, -1])
    bus_2 = pp.create_bus(net, name="bus 2", vn_kv=20, type='b',
                          geodata=[-0.5, -2])
    bus_3 = pp.create_bus(net, name="bus 3", vn_kv=20, type='b',
                          geodata=[-0.5, -3])
    bus_4 = pp.create_bus(net, name="bus 4", vn_kv=20, type='b',
                          geodata=[-0.5, -4])
    bus_5 = pp.create_bus(net, name="bus 5", vn_kv=20, type='b',
                          geodata=[0.5, -4])
    bus_6 = pp.create_bus(net, name="bus 6", vn_kv=20, type='b',
                          geodata=[0.5, -3])

    pp.create_ext_grid(net, 0, vm_pu=1)

    pp.create_line(net, name="line 0", from_bus=bus_mv, to_bus=bus_2,
                   length_km=1,
                   std_type="NA2XS2Y 1x185 RM/25 12/20 kV")
    pp.create_line(net, name="line 1", from_bus=bus_2, to_bus=bus_3,
                   length_km=1,
                   std_type="NA2XS2Y 1x185 RM/25 12/20 kV")
    line_2 = pp.create_line(net, name="line 2", from_bus=bus_3, to_bus=bus_4,
                            length_km=1,
                            std_type="NA2XS2Y 1x185 RM/25 12/20 kV")
    line_3 = pp.create_line(net, name="line 3", from_bus=bus_4, to_bus=bus_5,
                            length_km=1,
                            std_type="NA2XS2Y 1x185 RM/25 12/20 kV")
    pp.create_line(net, name="line 4", from_bus=bus_5, to_bus=bus_6,
                   length_km=1,
                   std_type="NA2XS2Y 1x185 RM/25 12/20 kV")
    pp.create_line(net, name="line 5", from_bus=bus_6, to_bus=bus_mv,
                   length_km=1,
                   std_type="NA2XS2Y 1x185 RM/25 12/20 kV")

    pp.create_transformer(net, hv_bus=bus_hv, lv_bus=bus_mv,
                          std_type="25 MVA 110/20 kV")

    pp.create_load(net, bus=bus_2, p_mw=50, q_mvar=compute_reactive_power(50),
                   name="load 0")
    pp.create_sgen(net, bus_2, p_mw=1, q_mvar=compute_reactive_power(1),
                   name="sgen 0")

    pp.create_load(net, bus_3, p_mw=50, q_mvar=compute_reactive_power(50),
                   name="load 1")
    pp.create_sgen(net, bus_3, p_mw=1, q_mvar=compute_reactive_power(1),
                   name="sgen 1")

    # dazwischen switch

    load_2 = pp.create_load(net, bus_4, p_mw=1,
                            q_mvar=compute_reactive_power(1), name="load 2")
    pp.create_sgen(net, bus_4, p_mw=160, q_mvar=compute_reactive_power(160),
                   name="sgen 2")

    load_3 = pp.create_load(net, bus_5, p_mw=1,
                            q_mvar=compute_reactive_power(1), name="load 3")
    pp.create_sgen(net, bus_5, p_mw=100, q_mvar=compute_reactive_power(100),
                   name="sgen 3")

    pp.create_load(net, bus_6, p_mw=1, q_mvar=compute_reactive_power(1),
                   name="load 4")
    pp.create_sgen(net, bus_6, p_mw=100, q_mvar=compute_reactive_power(100),
                   name="sgen 4")

    pp.create_switch(net, bus_3, line_2, et='l', closed=True,
                     type='LBS')
    # pp.create_switch(net, bus_4, line_2, et='l', closed=False,
    #                  type='LBS')
    return net

# try:
#     pp.runpp(net, numba=True)
# except:
#     print('did not converge')
#
# for time, power_value in zip(dates, power):
#     net['sgen'].loc[2,
#                     'p_mw'] = power_value
#     q = compute_reactive_power(power_value)
#     net['sgen'].loc[2,
#                     'q_mvar'] = q
#     try:
#         pp.runpp(net, numba=True)
#     except:
#         print(time)