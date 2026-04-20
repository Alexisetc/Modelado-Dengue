%Marini 
function psi1B = psi1_b(day)
    global P 
    %Coordinates used for coefficient fit
    %x_values = [10, 15, 25, 30];
    %y_values = [2, 4.5, 7.4, 6.7];
    coefficients = [-0.0007, 0.0227, 0.2817, -2.3500];
    x_values=temp(day, 0);
    psi1B = polyval(coefficients, x_values);
    %plot(linspace(13, 33, 40), polyval((coefficients), (linspace(13, 33, 40))))
end