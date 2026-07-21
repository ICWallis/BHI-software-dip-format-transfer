GLOG to WCL Conversion

Sticks  Working method 
Dips    Working method


WCL to GLOG Conversion

Sticks  Working method. 
        Just need to export CALA and this in tip azi calculation. Method current assumes single BH radius. 

Dips    Working method
        WCL allows more than one visible azimuth range while GLOG does not.
        The method currently assumes that only one visible azimuth range is present.
        In future, build a test for multiple visible azimuth ranges. Then either:
            (A) Discard the narrowest range
            (B) Make a duplicate sinusoid with the second visible azimuth range in it (preferred)
        
