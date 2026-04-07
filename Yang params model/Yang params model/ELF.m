clearvars
% close all
clc

global P

my_parameters;

Ga0 = P.bF_a * (P.psi1_a(1)/(P.mu_E_a(1) + P.psi1_a(1)))*(P.psi2_a(1)/(P.mu_L_a(1) + P.psi2_a(1))) * (P.phi_p_a(1)/P.mu_F_a(1));
La0 = P.K * (1 - (1/Ga0));
Fa0 = P.bF_a * (P.psi2_a(1)/P.mu_F_a(1)) * La0;
Ea0 = P.bF_a * (P.phi_p_a(1)/(P.mu_E_a(1) + P.psi1_a(1))) * (P.psi2_a(1)/P.mu_F_a(1)) * La0;

%Gb0 = P.bF_b * (P.psi1_b(1)/(P.mu_E_b(1) + P.psi1_b(1)))*(P.psi2_b(1)/(P.mu_L_b(1) + P.psi2_b(1))) * (P.phi_p_b(1)/P.mu_F_b(1));
%Lb0 = P.K * (1 - (1/Gb0));
%Fb0 = P.bF_b * (P.psi2_b(1)/P.mu_F_b(1)) * Lb0;
%Eb0 = P.bF_b * (P.phi_p_b(1)/(P.mu_E_b(1) + P.psi1_b(1))) * (P.psi2_b(1)/P.mu_F_b(1)) * Lb0;


y0 = [Ea0;La0;Fa0;10;0;0]; % initial condition
tfinal = 365*1;
tspan = linspace(0,tfinal,100); % output time points

[t,y] = ode45(@(t,y) myODE_ELF(t,y), tspan, y0); % solve for solution
Ea = y(:,1); La = y(:,2); Fa = y(:,3); 
Eb = y(:,4); Lb = y(:,5); Fb = y(:,6);

AE_tot_a=Ea+La+Fa;
AE_tot_b=Eb+Lb+Fb;

% % plotting
% figure_setups; hold on
% plot(t,Ea,'r-',t,La,'g--',t, Fa,'b-.')
% plot(t,Eb,'c-',t,Lb,'m--',t, Fb,'y-.')
% xlabel('t')
% % Set Y-axis limits
% ylim([0, 800000]); 
% legend('Ea','La','Fa','Eb','Lb','Fb')

Ea_frac=Ea./AE_tot_a;
La_frac=La./AE_tot_a;
Fa_frac=Fa./AE_tot_a;

Eb_frac=Eb./AE_tot_b;
Lb_frac=Lb./AE_tot_b;
Fb_frac=Fb./AE_tot_b;


% plotting
figure_setups; hold on
plot(t,Ea_frac,'r-',t,La_frac,'g--',t, Fa_frac,'b-.')
plot(t,Eb_frac,'c-',t,Lb_frac,'m--',t, Fb_frac,'y-.')
xlabel('t')
% Set Y-axis limits
%ylim([0, 0.09]); 
legend('Ea frac','La frac','Fa frac','Eb','Lb','Fb')



%T=16:1:32;
%mu_V=0.8692-0.159*T+0.01116*T.^2;


