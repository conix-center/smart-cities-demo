import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..','wave','python'))
import client
import time
from enum import Enum, auto
import pint

class ConixPoster:

    def __init__(self, client_id, domain_url = 'stream.conixdb.io', domain_username='conix', domain_password='stream', domain_port='8883'):
        #start up a conix client
        self.client = client.Client(str(client_id),
            mosquitto_url=domain_url,
            mosquitto_pass=domain_password,
            mosquitto_user=domain_username,
            mosquitto_port=domain_port,
            mosquitto_tls = True)

        self.registrationMap = {}
        self.sensorTypes = self.SensorTypes()

    """
    This post sensor data to conix in the right format

    sensor_uuid - some unique string identifying a sensor
    sensor - the type of sensor you are posting. must be of type ConixPoster.SensorTypes
    value - the value of the sensor. Can be number or text
    unit - A string of a standard unit or a pint unit object. raises unit error on failure
    timestamp - microsecond epoch time. Optionally. Excluding will set to now
    """
    def post(self, sensor_uuid, sensor, value, unit, timestamp=None):

        #is this a valid sensor type?
        if not isinstance(sensor,self.SensorTypes):
            raise TypeError("sensor must by a predefined sensor type. Find your sensor type in sensortypes.py or add one if it doesn't exist.")

        parsed_unit = None
        if not isinstance(unit, pint.UnitRegistry()):
            #check if we can resolve the unit string
            ureg = UnitRegistry()
            parsed_unit = ureg.parse_unit(unit)

        #do we know about this sensor uuid?
        if sensor_uuid not in self.registrationMap:
            try:
                namespace = self.client.register(sensor_uuid)
                self.registrationMap[sensor_uuid] = namespace
            except TimeoutError as e:
                print(e)
                print("Maybe the registration server is down?")
                return

        message = {}
        message['UUID'] = sensor_uuid
        message['value'] = value
        message['channel'] = str(sensor)
        message['unit'] = str(parsed_unit)
        if timestamp is not None:
            message['timestamp'] = timestamp
        else:
            message['timestamp'] = int(round(time.time()*100000))

        self.client.publish(self.registrationMap[sensor_uuid],sensor_uuid + '/' + str(sensor), message)

    class SensorTypes(Enum):
        Zone_Temperature_Sensor = auto()
        Zone_Humidity_Sensor = auto()
        Zone_Air_Temperature_Sensor = auto()
        Yearly_Steam_Usage_Sensor = auto()
        Wind_Speed_Sensor = auto()
        Wind_Direction_Sensor = auto()
        Weather_Wind_Speed_Sensor = auto()
        Weather_Wind_Direction_Sensor = auto()
        Weather_Temperature_Sensor = auto()
        Weather_Solar_Radiance_Sensor = auto()
        Weather_Relative_Humidity_Sensor = auto()
        Weather_Rain_Sensor = auto()
        Weather_Rain_Duration_Sensor = auto()
        Weather_Outside_Enthalpy_Sensor = auto()
        Weather_Hail_Sensor = auto()
        Weather_Cloud_Height_Sensor = auto()
        Weather_Cloud_Coverage_Sensor = auto()
        Water_Usage_Sensor = auto()
        Water_System_Water_Supply_Temperature_Sensor = auto()
        Water_System_Water_Discharge_Temperature_Sensor = auto()
        Water_System_Deionised_Water_Level_Sensor = auto()
        Water_System_Deionised_Water_Conductivity_Sensor = auto()
        Water_System_DI_Water_Level_Sensor = auto()
        Water_Supply_Temperature_Sensor = auto()
        Water_Level_Sensor = auto()
        Water_Flow_Sensor = auto()
        Water_Discharge_Temperature_Sensor = auto()
        Warmest_Zone_Temperature_Sensor = auto()
        Warm_Cool_Adjust_Sensor = auto()
        Voltage_Sensor = auto()
        Velocity_Pressure_Sensor = auto()
        Valve_Pressure_Sensor = auto()
        VFD_Speed_Sensor = auto()
        VFD_Running_Hour_Sensor = auto()
        VFD_Run_Time_Sensor = auto()
        VFD_Output_Voltage_Sensor = auto()
        VFD_Output_Frequency_Sensor = auto()
        VFD_On_Timer_Sensor = auto()
        VFD_Motor_Torque_Sensor = auto()
        VFD_Motor_Speed_Sensor = auto()
        VFD_Motor_Current_Sensor = auto()
        VFD_Load_Current_Sensor = auto()
        VFD_Energy_Sensor = auto()
        VFD_Drive_Temperature_Sensor = auto()
        VFD_DC_Bus_Voltage_Sensor = auto()
        VFD_Current_Sensor = auto()
        VAV_Zone_Temperature_Sensor = auto()
        VAV_Zone_Air_Temperature_Sensor = auto()
        VAV_Warm_Cool_Adjust_Sensor = auto()
        VAV_Thermostat_Adjust_Sensor = auto()
        VAV_Supply_Air_Velocity_Pressure_Sensor = auto()
        VAV_Supply_Air_Temperature_Sensor = auto()
        VAV_Supply_Air_Flow_Sensor = auto()
        VAV_Room_Temperature_Sensor = auto()
        VAV_Return_Air_Temperature_Sensor = auto()
        VAV_Occupancy_Sensor = auto()
        VAV_Discharge_Air_Velocity_Pressure_Sensor = auto()
        VAV_Discharge_Air_Temperature_Sensor = auto()
        VAV_Discharge_Air_Flow_Sensor = auto()
        VAV_Damper_Position_Sensor = auto()
        VAV_CO2_Sensor = auto()
        VAV_CO2_Level_Sensor = auto()
        VAV_Booster_Fan_Air_Flow_Sensor = auto()
        Usage_Sensor = auto()
        Underfloor_Temperature_Sensor = auto()
        Trace_Heat_Sensor = auto()
        Torque_Sensor = auto()
        Today_Steam_Usage_Sensor = auto()
        Timer_Sensor = auto()
        Thermostat_Adjust_Sensor = auto()
        Thermal_Power_Sensor = auto()
        Temperature_Sensor = auto()
        Supply_Water_Temperature_Sensor = auto()
        Supply_Water_Flow_Sensor = auto()
        Supply_Fan_VFD_Speed_Sensor = auto()
        Supply_Fan_Piezoelectric_Sensor = auto()
        Supply_Fan_Fan_Air_Flow_Sensor = auto()
        Supply_Fan_Differential_Pressure_Sensor = auto()
        Supply_Fan_Cooling_Coil_Valve_Pressure_Sensor = auto()
        Supply_Fan_Air_Flow_Sensor = auto()
        Supply_Air_Velocity_Pressure_Sensor = auto()
        Supply_Air_Temperature_Sensor = auto()
        Supply_Air_Static_Pressure_Sensor = auto()
        Supply_Air_Humidity_Sensor = auto()
        Supply_Air_Flow_Sensor = auto()
        Steam_Usage_Sensor = auto()
        Static_Pressure_Sensor = auto()
        Speed_Sensor = auto()
        Solar_Zenith_Angle_Sensor = auto()
        Solar_Radiance_Sensor = auto()
        Solar_Panel_Solar_Zenith_Angle_Sensor = auto()
        Solar_Panel_Solar_Azimuth_Angle_Sensor = auto()
        Solar_Panel_Photovoltaic_Current_Output_Sensor = auto()
        Solar_Panel_PV_Current_Output_Sensor = auto()
        Solar_Panel_Battery_Voltage_Sensor = auto()
        Solar_Azimuth_Angle_Sensor = auto()
        Running_Hour_Sensor = auto()
        Run_Time_Sensor = auto()
        Room_Temperature_Sensor = auto()
        Return_Water_Temperature_Sensor = auto()
        Return_Fan_VFD_Speed_Sensor = auto()
        Return_Fan_Fan_Air_Flow_Sensor = auto()
        Return_Fan_Differential_Speed_Sensor = auto()
        Return_Fan_Air_Flow_Sensor = auto()
        Return_Air_Temperature_Sensor = auto()
        Return_Air_Humidity_Sensor = auto()
        Return_Air_Grains_Sensor = auto()
        Return_Air_Flow_Sensor = auto()
        Return_Air_Enthalpy_Sensor = auto()
        Return_Air_Dewpoint_Sensor = auto()
        Return_Air_CO2_Sensor = auto()
        Relative_Humidity_Sensor = auto()
        Rain_Sensor = auto()
        Rain_Duration_Sensor = auto()
        Pressure_Sensor = auto()
        Preheat_Supply_Air_Temperature_Sensor = auto()
        Preheat_Discharge_Air_Temperature_Sensor = auto()
        Preheat_Coil_Leaving_Water_Temperature_Sensor = auto()
        Preheat_Coil_Entering_Air_Temperature_Sensor = auto()
        Power_System_Peak_Power_Demand_Sensor = auto()
        Power_Sensor = auto()
        Piezoelectric_Sensor = auto()
        Photovoltaic_Current_Output_Sensor = auto()
        Peak_Power_Demand_Sensor = auto()
        PV_Current_Output_Sensor = auto()
        PIR_Sensor = auto()
        Outside_Luminance_Sensor = auto()
        Outside_Enthalpy_Sensor = auto()
        Outside_Air_Temperature_Sensor = auto()
        Outside_Air_Lockout_Temperature_Differential_Sensor = auto()
        Outside_Air_Humidity_Sensor = auto()
        Outside_Air_Grains_Sensor = auto()
        Outside_Air_Flow_Sensor = auto()
        Outside_Air_Enthalpy_Sensor = auto()
        Outside_Air_Dewpoint_Sensor = auto()
        Outside_Air_Damper_Position_Sensor = auto()
        Outside_Air_CO2_Sensor = auto()
        Output_Voltage_Sensor = auto()
        Output_Frequency_Sensor = auto()
        On_Timer_Sensor = auto()
        Occupancy_Sensor = auto()
        Motor_Torque_Sensor = auto()
        Motor_Speed_Sensor = auto()
        Motor_Power_Sensor = auto()
        Motor_Current_Sensor = auto()
        Motion_Sensor = auto()
        Monthly_Steam_Usage_Sensor = auto()
        Mixed_Air_Temperature_Sensor = auto()
        Mixed_Air_Damper_Position_Sensor = auto()
        Medium_Temperature_Hot_Water_Supply_Temperature_Sensor = auto()
        Medium_Temperature_Hot_Water_Return_Temperature_Sensor = auto()
        Medium_Temperature_Hot_Water_Discharge_Temperature_Sensor = auto()
        Medium_Temperature_Hot_Water_Differential_Pressure_Sensor = auto()
        Luminance_Sensor = auto()
        Lowest_Zone_Temperature_Sensor = auto()
        Lowest_Exhaust_Air_Static_Pressure_Sensor = auto()
        Low_Outside_Air_Temperature_Enable_Differential_Sensor = auto()
        Load_Current_Sensor = auto()
        Lighting_System_Luminance_Sensor = auto()
        Leaving_Water_Temperature_Sensor = auto()
        Illumination_Sensor = auto()
        Ice_Tank_Leaving_Water_Temperature_Sensor = auto()
        Ice_Tank_Entering_Water_Temperature_Sensor = auto()
        Humidity_Sensor = auto()
        Hot_Water_Usage_Sensor = auto()
        Hot_Water_Supply_Temperature_Sensor = auto()
        Hot_Water_Return_Temperature_Sensor = auto()
        Hot_Water_Flow_Sensor = auto()
        Hot_Water_Discharge_Temperature_Sensor = auto()
        Hot_Water_Differential_Pressure_Sensor = auto()
        Hot_Water_Coil_Entering_Temperature_Sensor = auto()
        Hot_Box_Temperature_Sensor = auto()
        Highest_Zone_Temperature_Sensor = auto()
        High_Temperature_Hot_Water_Supply_Temperature_Sensor = auto()
        High_Temperature_Hot_Water_Return_Temperature_Sensor = auto()
        High_Temperature_Hot_Water_Discharge_Temperature_Sensor = auto()
        Heating_Thermal_Power_Sensor = auto()
        Heat_Wheel_Voltage_Sensor = auto()
        Heat_Wheel_Supply_Air_Temperature_Sensor = auto()
        Heat_Wheel_Speed_Sensor = auto()
        Heat_Wheel_Discharge_Air_Temperature_Sensor = auto()
        Heat_Wheel_Differential_Pressure_Sensor = auto()
        Heat_Exchanger_Supply_Water_Temperature_Sensor = auto()
        Heat_Exchanger_Discharge_Water_Temperature_Sensor = auto()
        Hail_Sensor = auto()
        HWS_Medium_Temperature_Hot_Water_Supply_Temperature_Sensor = auto()
        HWS_Medium_Temperature_Hot_Water_Return_Temperature_Sensor = auto()
        HWS_Medium_Temperature_Hot_Water_Discharge_Temperature_Sensor = auto()
        HWS_Medium_Temperature_Hot_Water_Differential_Pressure_Sensor = auto()
        HWS_Hot_Water_Supply_Temperature_Sensor = auto()
        HWS_Hot_Water_Return_Temperature_Sensor = auto()
        HWS_Hot_Water_Discharge_Temperature_Sensor = auto()
        HWS_Hot_Water_Differential_Pressure_Sensor = auto()
        HWS_Hot_Water_Coil_Entering_Temperature_Sensor = auto()
        HWS_High_Temperature_Hot_Water_Supply_Temperature_Sensor = auto()
        HWS_High_Temperature_Hot_Water_Return_Temperature_Sensor = auto()
        HWS_High_Temperature_Hot_Water_Discharge_Temperature_Sensor = auto()
        HWS_Heat_Exchanger_Supply_Water_Temperature_Sensor = auto()
        HWS_Heat_Exchanger_Discharge_Water_Temperature_Sensor = auto()
        HVAC_Warmest_Zone_Temperature_Sensor = auto()
        HVAC_Lowest_Zone_Temperature_Sensor = auto()
        HVAC_Highest_Zone_Temperature_Sensor = auto()
        HVAC_Coldest_Zone_Temperature_Sensor = auto()
        HVAC_Average_Zone_Temperature_Sensor = auto()
        HVAC_Average_Supply_Air_Flow_Sensor = auto()
        HVAC_Average_Discharge_Air_Flow_Sensor = auto()
        HVAC_Average_Cooling_Demand_Sensor = auto()
        Gas_Usage_Sensor = auto()
        Fume_Hood_Sash_Position_Sensor = auto()
        Fume_Hood_Air_Flow_Sensor = auto()
        Frost_Sensor = auto()
        Frequency_Sensor = auto()
        Freezer_Temperature_Sensor = auto()
        Flow_Sensor = auto()
        Filter_Differential_Pressure_Sensor = auto()
        Fan_Air_Flow_Sensor = auto()
        FCU_Zone_Temperature_Sensor = auto()
        FCU_Zone_Air_Temperature_Sensor = auto()
        FCU_Supply_Fan_VFD_Speed_Sensor = auto()
        FCU_Supply_Air_Temperature_Sensor = auto()
        FCU_Run_Time_Sensor = auto()
        FCU_Return_Fan_VFD_Speed_Sensor = auto()
        FCU_Return_Air_Temperature_Sensor = auto()
        FCU_Return_Air_Humidity_Sensor = auto()
        FCU_Return_Air_CO2_Sensor = auto()
        FCU_Humidity_Sensor = auto()
        FCU_Discharge_Fan_VFD_Speed_Sensor = auto()
        FCU_Discharge_Air_Temperature_Sensor = auto()
        FCU_Chilled_Valve_Pressure_Sensor = auto()
        FCU_CO2_Sensor = auto()
        Exhaust_Fan_Piezoelectric_Sensor = auto()
        Exhaust_Fan_Fan_Air_Flow_Sensor = auto()
        Exhaust_Air_Velocity_Pressure_Sensor = auto()
        Exhaust_Air_Temperature_Sensor = auto()
        Exhaust_Air_Static_Pressure_Sensor = auto()
        Exhaust_Air_Stack_Flow_Sensor = auto()
        Exhaust_Air_Humidity_Sensor = auto()
        Exhaust_Air_Flow_Sensor = auto()
        Environment_Box_Temperature_Sensor = auto()
        Enthalpy_Sensor = auto()
        Entering_Water_Temperature_Sensor = auto()
        Energy_Sensor = auto()
        Electricity_Power_Sensor = auto()
        Electricity_Energy_Sensor = auto()
        Drive_Temperature_Sensor = auto()
        Domestic_Hot_Water_Supply_Temperature_Sensor = auto()
        Domestic_Hot_Water_Discharge_Temperature_Sensor = auto()
        Discharge_Fan_VFD_Speed_Sensor = auto()
        Discharge_Fan_Piezoelectric_Sensor = auto()
        Discharge_Fan_Air_Flow_Sensor = auto()
        Discharge_Air_Velocity_Pressure_Sensor = auto()
        Discharge_Air_Temperature_Sensor = auto()
        Discharge_Air_Static_Pressure_Sensor = auto()
        Discharge_Air_Humidity_Sensor = auto()
        Discharge_Air_Flow_Sensor = auto()
        Direction_Sensor = auto()
        Differential_Temperature_Sensor = auto()
        Differential_Speed_Sensor = auto()
        Differential_Pressure_Sensor = auto()
        Dewpoint_Sensor = auto()
        Demand_Sensor = auto()
        Deionised_Water_Level_Sensor = auto()
        Deionised_Water_Conductivity_Sensor = auto()
        Damper_Position_Sensor = auto()
        DI_Water_Level_Sensor = auto()
        DHWS_Domestic_Hot_Water_Supply_Temperature_Sensor = auto()
        DHWS_Domestic_Hot_Water_Discharge_Temperature_Sensor = auto()
        DC_Bus_Voltage_Sensor = auto()
        Current_Steam_Usage_Sensor = auto()
        Current_Sensor = auto()
        Cooling_Thermal_Power_Sensor = auto()
        Cooling_Coil_Valve_Pressure_Sensor = auto()
        Cooling_Coil_Supply_Air_Temperature_Sensor = auto()
        Cooling_Coil_Discharge_Air_Temperature_Sensor = auto()
        Conductivity_Sensor = auto()
        Condensor_Temperature_Sensor = auto()
        Condenser_Condensor_Temperature_Sensor = auto()
        Coldest_Zone_Temperature_Sensor = auto()
        Cold_Box_Temperature_Sensor = auto()
        Chiller_Run_Time_Sensor = auto()
        Chiller_On_Timer_Sensor = auto()
        Chilled_Water_Usage_Sensor = auto()
        Chilled_Water_Temperature_Differential_Sensor = auto()
        Chilled_Water_Supply_Temperature_Sensor = auto()
        Chilled_Water_Supply_Flow_Sensor = auto()
        Chilled_Water_Return_Temperature_Sensor = auto()
        Chilled_Water_Flow_Sensor = auto()
        Chilled_Water_Discharge_Temperature_Sensor = auto()
        Chilled_Water_Discharge_Flow_Sensor = auto()
        Chilled_Water_Differential_Pressure_Sensor = auto()
        Chilled_Valve_Pressure_Sensor = auto()
        Capacity_Sensor = auto()
        CWS_Chilled_Water_Temperature_Differential_Sensor = auto()
        CWS_Chilled_Water_Supply_Temperature_Sensor = auto()
        CWS_Chilled_Water_Supply_Flow_Sensor = auto()
        CWS_Chilled_Water_Return_Temperature_Sensor = auto()
        CWS_Chilled_Water_Discharge_Temperature_Sensor = auto()
        CWS_Chilled_Water_Discharge_Flow_Sensor = auto()
        CWS_Chilled_Water_Differential_Pressure_Sensor = auto()
        CRAC_Zone_Humidity_Sensor = auto()
        CRAC_Temperature_Sensor = auto()
        CRAC_Humidity_Sensor = auto()
        CRAC_Capacity_Sensor = auto()
        CO2_Sensor = auto()
        CO2_Level_Sensor = auto()
        CO2_Differential_Sensor = auto()
        Bypass_Damper_Position_Sensor = auto()
        Bypass_Air_Flow_Sensor = auto()
        Building_Static_Pressure_Sensor = auto()
        Booster_Fan_Air_Flow_Sensor = auto()
        Boiler_Run_Time_Sensor = auto()
        Battery_Voltage_Sensor = auto()
        Average_Zone_Temperature_Sensor = auto()
        Average_Supply_Air_Flow_Sensor = auto()
        Average_Exhaust_Air_Static_Pressure_Sensor = auto()
        Average_Discharge_Air_Flow_Sensor = auto()
        Average_Cooling_Demand_Sensor = auto()
        Angle_Sensor = auto()
        Ambient_Illumination_Sensor = auto()
        Air_Grains_Sensor = auto()
        Air_Flow_Sensor = auto()
        AHU_Zone_Temperature_Sensor = auto()
        AHU_Zone_Air_Temperature_Sensor = auto()
        AHU_Warmest_Zone_Temperature_Sensor = auto()
        AHU_Underfloor_Temperature_Sensor = auto()
        AHU_Trace_Heat_Sensor = auto()
        AHU_Supply_Fan_VFD_Speed_Sensor = auto()
        AHU_Supply_Fan_Piezoelectric_Sensor = auto()
        AHU_Supply_Fan_Air_Flow_Sensor = auto()
        AHU_Supply_Air_Temperature_Sensor = auto()
        AHU_Supply_Air_Static_Pressure_Sensor = auto()
        AHU_Supply_Air_Humidity_Sensor = auto()
        AHU_Static_Pressure_Sensor = auto()
        AHU_Run_Time_Sensor = auto()
        AHU_Return_Fan_VFD_Speed_Sensor = auto()
        AHU_Return_Fan_Differential_Speed_Sensor = auto()
        AHU_Return_Fan_Air_Flow_Sensor = auto()
        AHU_Return_Air_Temperature_Sensor = auto()
        AHU_Return_Air_Humidity_Sensor = auto()
        AHU_Return_Air_Grains_Sensor = auto()
        AHU_Return_Air_Flow_Sensor = auto()
        AHU_Return_Air_Enthalpy_Sensor = auto()
        AHU_Return_Air_Dewpoint_Sensor = auto()
        AHU_Return_Air_CO2_Sensor = auto()
        AHU_Preheat_Supply_Air_Temperature_Sensor = auto()
        AHU_Preheat_Discharge_Air_Temperature_Sensor = auto()
        AHU_Preheat_Coil_Entering_Air_Temperature_Sensor = auto()
        AHU_Outside_Air_Temperature_Sensor = auto()
        AHU_Outside_Air_Lockout_Temperature_Differential_Sensor = auto()
        AHU_Outside_Air_Humidity_Sensor = auto()
        AHU_Outside_Air_Grains_Sensor = auto()
        AHU_Outside_Air_Flow_Sensor = auto()
        AHU_Outside_Air_Enthalpy_Sensor = auto()
        AHU_Outside_Air_Dewpoint_Sensor = auto()
        AHU_Outside_Air_Damper_Position_Sensor = auto()
        AHU_Outside_Air_CO2_Sensor = auto()
        AHU_Mixed_Air_Temperature_Sensor = auto()
        AHU_Mixed_Air_Damper_Position_Sensor = auto()
        AHU_Lowest_Zone_Temperature_Sensor = auto()
        AHU_Lowest_Exhaust_Air_Static_Pressure_Sensor = auto()
        AHU_Low_Outside_Air_Temperature_Enable_Differential_Sensor = auto()
        AHU_Highest_Zone_Temperature_Sensor = auto()
        AHU_Heat_Wheel_Voltage_Sensor = auto()
        AHU_Heat_Wheel_Supply_Air_Temperature_Sensor = auto()
        AHU_Heat_Wheel_Speed_Sensor = auto()
        AHU_Heat_Wheel_Discharge_Air_Temperature_Sensor = auto()
        AHU_Heat_Wheel_Differential_Pressure_Sensor = auto()
        AHU_Frost_Sensor = auto()
        AHU_Exhaust_Fan_Piezoelectric_Sensor = auto()
        AHU_Exhaust_Air_Velocity_Pressure_Sensor = auto()
        AHU_Exhaust_Air_Temperature_Sensor = auto()
        AHU_Exhaust_Air_Static_Pressure_Sensor = auto()
        AHU_Exhaust_Air_Stack_Flow_Sensor = auto()
        AHU_Exhaust_Air_Humidity_Sensor = auto()
        AHU_Exhaust_Air_Flow_Sensor = auto()
        AHU_Discharge_Fan_VFD_Speed_Sensor = auto()
        AHU_Discharge_Fan_Piezoelectric_Sensor = auto()
        AHU_Discharge_Fan_Air_Flow_Sensor = auto()
        AHU_Discharge_Air_Temperature_Sensor = auto()
        AHU_Discharge_Air_Static_Pressure_Sensor = auto()
        AHU_Discharge_Air_Humidity_Sensor = auto()
        AHU_Differential_Pressure_Sensor = auto()
        AHU_Cooling_Coil_Supply_Air_Temperature_Sensor = auto()
        AHU_Cooling_Coil_Discharge_Air_Temperature_Sensor = auto()
        AHU_Coldest_Zone_Temperature_Sensor = auto()
        AHU_CO2_Differential_Sensor = auto()
        AHU_Bypass_Damper_Position_Sensor = auto()
        AHU_Bypass_Air_Flow_Sensor = auto()
        AHU_Building_Static_Pressure_Sensor = auto()
        AHU_Average_Zone_Temperature_Sensor = auto()
        AHU_Average_Exhaust_Air_Static_Pressure_Sensor = auto()
