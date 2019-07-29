class Communication(object):
    @classmethod
    def get_request_body(
            cls, sensora_time, sensora_value, sensorb_time, sensorb_value, device_id, current_water_amount,
            max_water_amount, max_water_time):
        return {
            'clientReadings':
                {
                    'sensorA': [{'created_at': sensora_time, 'value': sensora_value}],
                    'sensorB': [{'created_at': sensorb_time, 'value': sensorb_value}]
                },
            'clientDevice': {
                "id": device_id,
                "current_water_amount": current_water_amount,
                "max_water_amount": {
                    "value": max_water_amount,
                    "created_at": max_water_time
                }
            }
        }
