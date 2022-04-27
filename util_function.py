import pandas as pd
import pandapower as pp
import numpy as np
import pandapower.networks as networks
import matplotlib.pyplot as plt

# https://pandapower.readthedocs.io/en/v2.9.0/networks/example.html

def compute_reactive_power(p_mw, cos_phi=0.97, operating_mode='inductive'):
    """Calculates reactive power according to given active power,
    power factor and operation mode
    :param p_mw: active power in mw
    :param cos_phi: power factor
    :param operating_mode: inductive or capacitive
    :return: reactive power q_mvar
    """
    abs_q = p_mw * np.tan(np.arccos(cos_phi))
    # current phase after voltage phase, draw reactive power
    if operating_mode == 'inductive':
        return abs_q
    # supply reactive power
    elif operating_mode == 'capacitive':
        return - abs_q


def create_net(switch_open=False):
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

    pp.create_switch(net, bus_3, line_2, et='l', closed=switch_open,
                     type='LBS')

    return net


# scenario
def run_simulation(net):
    csv = pd.read_csv('pv.csv', delimiter=';',
                      encoding="utf-8-sig")
    dates = csv["Datum"].tolist()
    power = csv["MW"].tolist()

    bus_values = []
    load_values = []
    sgen_values = []
    sgen_2_values = []
    sgen_index = 2

    for time, power_value in zip(dates, power):
        net['sgen'].loc[sgen_index,
                        'p_mw'] = power_value
        q = compute_reactive_power(power_value)
        net['sgen'].loc[sgen_index,
                        'q_mvar'] = q
        try:
            pp.runpp(net, numba=True)
        except:
            pass
        res_vmpu = net['res_bus']['vm_pu'].tolist()
        for idx in range(len(res_vmpu)):
            if np.isnan(res_vmpu[idx]):
                res_vmpu[idx] = 0
            # res_vmpu[idx] = abs(res_[idx])
        bus_values.append(np.mean(res_vmpu))

        res_load = net['res_load']['p_mw'].tolist()
        for idx in range(len(res_load)):
            if np.isnan(res_load[idx]):
                res_load[idx] = 0
            # res_vmpu[idx] = abs(res_[idx])
        load_values.append(np.mean(res_load))

        res_sgen = net['res_sgen']['p_mw'].tolist()
        for idx in range(len(res_sgen)):
            if np.isnan(res_sgen[idx]):
                res_sgen[idx] = 0
            # res_sgen[idx] = abs(res_[idx])
        sgen_values.append(np.mean(res_sgen))

        res_sgen_2 = net['res_sgen']['p_mw'][sgen_index].tolist()
        if np.isnan(res_sgen_2):
            res_sgen_2 = 0
        sgen_2_values.append(res_sgen_2)
    return dates, bus_values, load_values, sgen_2_values, sgen_2_values

plt.plot(dates, bus_values)
plt.xlabel('Zeit')
plt.ylabel('Spannungswerte')
plt.title('Spannung der Busse')
# function to show the plot
plt.show()


plt.plot(dates, load_values)
plt.xlabel('Zeit')
plt.ylabel('Leistung')
plt.title('Leistungswerte der Lasten')

# function to show the plot
plt.show()

plt.plot(dates, sgen_values)
plt.xlabel('Zeit')
plt.ylabel('Leistung')
plt.title('Leistungswerte der Generatoren')

# function to show the plot
plt.show()

plt.plot(dates, sgen_2_values)
plt.xlabel('Zeit')
plt.ylabel('Leistung')
plt.title('Leistungswerte Generator 2')

# function to show the plot
plt.show()

# Fahrplanwerte
plt.plot(dates, sgen_2_values)
plt.xlabel('Zeit')
plt.ylabel('Leistung')
plt.title('Fahrplanwerte Generator 2')

# function to show the plot
plt.show()
