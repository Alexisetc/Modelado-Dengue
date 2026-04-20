%We read in the weekly temperature, interpolate the daily temperature, and
%finally smooths the curve. 
function periodic_temp = temp(day, method)
    global P
    
    if method == 1
    %These parameters were obtained from the script periodic_temperature
    %mdl1
    So=29.45;
    c=0.8218;
    k1=0.7757;
    k2=0;
    u1=1.546e-08;
    u2=0;
    v=0.08216;
    white_fcn0 = (So.*(c+v.*(1-c).*(0.5.*(1+cos(2.*pi.*((day+90)./365-u1)))).^k1+(1-v).*(1-c).*(0.5.*(1+cos(2.*pi.*(day./365-u2)))).^k2));
    periodic_temp = white_fcn0;
    else
    %These parameters were obtained from the script periodic_temperature
    %mdl4
    So=27.04;
    c=0.8949;
    k1=0.7757;
    k2=0;
    u1=2.335e-14;
    u2=0;
    v=0.1516;
    griffin_fcn0 = (So.*(c+v.*(1-c).*(0.5.*(1+cos(2.*pi.*((day+90)./365-u1)))).^k1));
    periodic_temp = griffin_fcn0;
    %periodic_temp = 25;
    end
end
