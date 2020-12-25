


def paradigm_selector(parent, paradigm):
    if paradigm == "MWM":
        from .mwm_panel import MWM
        return MWM(parent)
    elif paradigm == "OFT":
        from .oft_panel import OFT
        return OFT(parent)
    elif paradigm == "EPM":
        from .epm_panel import EPM
        return EPM(parent)
    elif paradigm == "Free":
        from .free_panel import Free
        return Free(parent)
    return None

