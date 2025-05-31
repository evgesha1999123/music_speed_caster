import platform

def osinfo():
    return {
        "system": platform.system(),
        "machine": platform.machine(),
        "platform": platform.platform(),
        "uname": platform.uname(),
    }

if __name__ == '__main__':
    print(osinfo())