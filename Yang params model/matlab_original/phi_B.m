function inter_fecundity = phi_B(day)
    global P 
    coeff_fecund = [0.0000116712819,-0.0015833228349,0.0854057774634,-02.3533940540695,35.0378012046865,-263.6780055767482,783.2335484007083];
    coeff_br = [0.000000038135089,-0.000005576944503,0.000324339154486,-0.009624903256283,0.153953856777874,-1.242444992921582,3.931227652768022];
    f_prod = @(x) polyval(coeff_br,x).*polyval(coeff_fecund,x);
    x_values=temp(day, 0);
    inter_fecundity = f_prod(x_values);
    %to plot function: plot(phi_A(1:569))
    %to plot the profile of the parameters vs temperature
    %plot(linspace(10, 40, 40), f_prod(linspace(10, 40, 40))) to plot temp dependent params
end
