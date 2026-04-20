%Marini cd '/Users/joanponce/Library/CloudStorage/Dropbox/Spatial Mosquito project/code/Yang params model'
function mu_E_b = muE_b(day)%shifted curve by 2.5 to remain positive
    global P 
    Egg_L1_coeffs = [-0.0002, 0.0139, -0.2278, 1.1650];
    dev_rate = [-0.0007, 0.0227, 0.2817, -2.3500];
    muE_b = @(x) polyval(dev_rate, x)./polyval(Egg_L1_coeffs,x)-polyval(dev_rate,x);
    x_values=temp(day, 0);
    mu_E_b = muE_b(x_values);
    %plot(linspace(13, 40, 40), muE_b(linspace(13, 40, 40)))
end