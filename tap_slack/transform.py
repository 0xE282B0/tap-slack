import types

def decimal_timestamp_to_utc_timestamp(timestamp):
    # Some timestamps returned by the Slack API are in the format of `Seconds.Milliseconds`
    # and this takes only the `Seconds` part of that timestamp.
    return timestamp.partition(".")[0]

def resolve(r):
    if isinstance(r, types.GeneratorType):
        return r
    else:
        return [r]

def transform_json(stream, data, date_fields, channel_id=None):
    result = []
    if data:
        for r in data:
            for record in resolve(r):
                if stream == "messages":
                    # Strip out file info and just keep id
                    file_ids = []
                    files = record.get("files", [])
                    for file in files:
                        file_id = file.get("id", None)
                        if file_id:
                            file_ids.append(file_id)
                    record['file_ids'] = file_ids

                if stream == "messages" or "threads":
                    # add channel_id to the message
                    record['channel_id'] = channel_id

                if stream == "channels":
                    # These come back on the client response but aren't actually populated
                    # Or in Slack's documentation at the time of writing, just remove them
                    record.pop("parent_conversation", None)
                    record.pop("channel_id", None)

                for date_field in date_fields:
                    timestamp = record.get(date_field, None)
                    if timestamp and isinstance(timestamp, str):
                        if stream == 'messages' or stream == "threads" and date_field == 'ts':
                            record['thread_ts'] = timestamp
                            record[date_field] = decimal_timestamp_to_utc_timestamp(timestamp)
                        else:
                            record[date_field] = decimal_timestamp_to_utc_timestamp(timestamp)
                result.append(record)
    return result
