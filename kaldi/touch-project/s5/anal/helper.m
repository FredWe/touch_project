classdef helper
    %UNTITLED2 Summary of this class goes here
    %   Detailed explanation goes here
    
    properties
        Property1
    end
    
    methods
        function [totdata, data_sil, data_nonsil] = load_data(data)
            data_sil = [];
            data_nonsil = [];
            fields = fieldnames(data);
            for idx = 1:length(fields)
                X = data.(fields{idx});
                if startsWith(fields{idx}, 'SIL')
                   data_sil = [data_sil; X];
                else
                   data_nonsil = [data_nonsil; X];
                end
            end
            totdata = [data_sil; data_nonsil];
        end

        function b = decorr_stretch(matin, a)
            m = mean(matin);
            Cov = cov(matin);
            SIGMA = diag(std(matin));
            [V, LAMBDA] = eig(Cov);
            S = diag(1./sqrt(diag(LAMBDA)));
            T = SIGMA * V * S * V';
            b = m + (a - m) * T;
        end

        function y = klt(matin, x)
            [V, D] = eig(cov(matin));
            d = x - mean(matin);
            delta_y = d * V;
            y = delta_y + mean(matin);
        end

        function plotout_corrcoef(matin, pltitle)
            imagesc(corrcoef(matin));
            colorbar;
            title(pltitle);
            print(sprintf('output/corrcoeff_%s', pltitle),'-dpng');
            mesh(corrcoef(matin));
            colorbar;
            title(pltitle);
            print(sprintf('output/mesh_corrcoeff_%s', pltitle),'-dpng');
        end

        function plotout_histogram(matin, pltitle)
            histogram(matin(:,2),'Normalization', 'probability')
            title(pltitle);
            print(sprintf('output/histogram_%s', pltitle),'-dpng');
            for ind = 1:size(matin, 2)
                histogram(matin(:,ind),'Normalization', 'probability')
                hold on;
            end
            title(pltitle);
            legend;
            print(sprintf('output/histogram_bydim_%s', pltitle),'-dpng');
            hold off;
        end

        function elbow_method(matin, maxk, pltitle)
            sse = zeros(1, maxk);
            for thisk = 1:maxk
                disp(thisk)
                [idx,C,sumd,D] = kmeans(matin, thisk);
                dists = D(sub2ind(size(D), 1:size(D, 1), idx'));
                sse(thisk) = sum(dists .^ 2);
            end
            semilogy(sse, '-*');
            title(pltitle);
            print(sprintf('output/sse_%s', pltitle),'-dpng');
        end
    end
end

