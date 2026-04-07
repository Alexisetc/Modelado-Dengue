function err = error_fun_betas(p)
    % Function to calculate the sum of squared errors between observed data and simulated model     

    % Initial conditions
    global P

    my_parameters;
    data = load('full_table_Lita.mat');

    Ga0 = P.bF_a * (P.psi1_a(1)/(P.mu_E_a(1) + P.psi1_a(1)))*(P.psi2_a(1)/(P.mu_L_a(1) + P.psi2_a(1))) * (P.phi_p_a(1)/P.mu_F_a(1));
    La0 = P.K * (1 - (1/Ga0));
    Fa0 = P.bF_a * (P.psi2_a(1)/P.mu_F_a(1)) * La0;
    Ea0 = P.bF_a * (P.phi_p_a(1)/(P.mu_E_a(1) + P.psi1_a(1))) * (P.psi2_a(1)/P.mu_F_a(1)) * La0;

    y01 = [Ea0;La0;Fa0;0;0;0]; % initial condition
    

    % Time span
    tfinal = [data.table_data.Days_Passed];
    tspan1 = linspace(0,355,355); %tspan1 = linspace(0,371,371);
    tspan2 = linspace(355,tfinal(end),918); % output time points tspan2 = linspace(372,tfinal(end),918);

    [t1,y1] = ode45(@(t,y) myODE_ELF(t,y,p), tspan1, y01); % solve for solution
    y02 = [y1(end,1);y1(end,2);y1(end,3);0;0;1];%40,36
    [t2,y2] = ode45(@(t,y) myODE_ELF(t,y,p), tspan2, y02);
    
    t = [t1;t2];
    y = [y1 ; y2];

    Ea = y(:,1); La = y(:,2); Fa = y(:,3); 
    Eb = y(:,4); Lb = y(:,5); Fb = y(:,6);

    AE_tot_a=Ea+La+Fa;
    AE_tot_b=Eb+Lb+Fb;

    Ea_frac=Ea./AE_tot_a;
    La_frac=La./AE_tot_a;
    Fa_frac=Fa./AE_tot_a;
    
    Eb_frac=Eb./AE_tot_b;
    Lb_frac=Lb./AE_tot_b;
    Fb_frac=Fb./AE_tot_b;


    figure_setups; hold on
    plot(t,Ea_frac,'r-',t,La_frac,'g--',t, Fa_frac,'b-.')
    plot(t,Eb_frac,'c-',t,Lb_frac,'m--',t, Fb_frac,'y-.')
    xlabel('t')
    % Set Y-axis limits
    %ylim([0, 0.09]); 
    legend('Ea frac','La frac','Fa frac','Eb','Lb','Fb')

    figure_setups; hold on
    plot(t(338:400),Ea_frac(338:400),'r-',t(338:400),La_frac(338:400),'g--',t(338:400), Fa_frac(338:400),'b-.')
    plot(t(338:400),Eb_frac(338:400),'c-',t(338:400),Lb_frac(338:400),'m--',t(338:400), Fb_frac(338:400),'y-.')
    xlabel('t')
    % Set Y-axis limits
    %ylim([0, 0.09]); 
    legend('Ea frac','La frac','Fa frac','Eb','Lb','Fb')
    
    % Switch to format long
    format long;
    disp(y2(1:10,:))
    format short;



     % Interpolate model output to match data times
    y_interp_aeg = interp1(tspan, y(:,2), data.Days_Passed, 'linear', 'extrap'); 
    y_interp_alb = interp1(tspan, y(:,5), data.Days_Passed, 'linear', 'extrap'); 

    % Calculate sum of squared errors
    err1 = sum((y_interp_aeg - data.Num_aeg).^2);
    err2 = sum((y_interp_alb - data.Num_alb).^2);
    %err = [err1; err2];
    err = err1;
end