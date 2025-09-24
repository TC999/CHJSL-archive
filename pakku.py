#coding=utf-8
import re
import sys

THRESHOLD = 15  # 秒
taolus = {
    '2333...': re.compile(r'^23{3,}$'),
    '6666...': re.compile(r'^6{4,}$'),
    'FFF...': re.compile(r'^[fF]+$'),
    'hhh...': re.compile(r'^[hH]+$'),
}

def taolu(text):
    for k, v in taolus.items():
        if v.match(text):
            return k
    return text

def parse_ass_events(lines):
    events = []
    for line in lines:
        if line.startswith('Dialogue:'):
            # Dialogue: 0,0:00:08.00,0:00:12.00,Default,,0,0,0,,弹幕内容
            parts = line.split(',', 9)
            if len(parts) > 9:
                start_time = parts[1]
                text = parts[9].strip()
                events.append((start_time, text, line))
    return events

def ass_time_to_seconds(ass_time):
    # ASS 时间格式: H:MM:SS.CS
    h, m, s = ass_time.split(':')
    s, cs = s.split('.')
    return int(h) * 3600 + int(m) * 60 + int(s) + int(cs) / 100

def process_events(events):
    hist = {}  # text : (time, count, last_line)
    filtered_lines = []
    cn = 0

    for start_time, text, line in events:
        t = ass_time_to_seconds(start_time)
        text = taolu(text)
        if text in hist and t - hist[text][0] > THRESHOLD:
            del hist[text]
        if text not in hist:
            hist[text] = [t, 1, line]
            filtered_lines.append(line)
        else:
            hist[text][1] += 1
            # 合并重复弹幕
            parts = line.split(',', 9)
            if len(parts) > 9:
                parts[9] = hist[text][2].split(',', 9)[9].strip() + ' [x%d]' % hist[text][1]
                merged_line = ','.join(parts)
                filtered_lines.remove(hist[text][2])
                filtered_lines.append(merged_line)
                hist[text][2] = merged_line
            cn += 1
    print('!! %d 弹幕被过滤' % cn)
    return filtered_lines

def main(input_path, output_path):
    with open(input_path, encoding='utf-8') as f:
        lines = f.readlines()

    # 找到 [Events] 段
    in_events = False
    output_lines = []
    event_lines = []
    for line in lines:
        if line.strip().startswith('[Events]'):
            in_events = True
            output_lines.append(line)
            continue
        if in_events:
            if line.startswith('Dialogue:'):
                event_lines.append(line)
            else:
                output_lines.append(line)
        else:
            output_lines.append(line)

    events = parse_ass_events(event_lines)
    filtered_event_lines = process_events(events)

    # 合并输出
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in output_lines:
            f.write(line)
        for line in filtered_event_lines:
            f.write(line)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('用法: python pakku_ass.py 输入.ass 输出.ass')
    else:
        main(sys.argv[1], sys.argv[2])