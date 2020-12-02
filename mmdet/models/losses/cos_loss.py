import torch
import torch.nn as nn
import torch.nn.functional as F


class CenterLoss(nn.Module):
    """Center loss.
    
    Reference:
    Wen et al. A Discriminative Feature Learning Approach for Deep Face Recognition. ECCV 2016.
    
    Args:
        num_classes (int): number of classes.
        feat_dim (int): feature dimension.
    """
    def __init__(self, num_classes=10, feat_dim=2, use_gpu=True):
        super(CenterLoss, self).__init__()
        self.num_classes = num_classes
        self.feat_dim = feat_dim
        self.use_gpu = use_gpu
            
        self.s = 30.0
        self.m = 0.4
#         self.loss_type = loss_type
#         self.in_features = in_features
#         self.out_features = out_features
        self.in_features = 1024
        self.out_features = 1024
        self.fc = nn.Linear(self.in_features, self.out_features, bias=False)
        self.eps = None
        if self.use_gpu:
            self.fc = self.fc.cuda()

    def forward(self, x, labels):
        """
        Args:
            x: feature matrix with shape (batch_size, feat_dim).
            labels: ground truth labels with shape (batch_size).
        """
#         batch_size = x.size(0)
#         distmat = torch.pow(x, 2).sum(dim=1, keepdim=True).expand(batch_size, self.num_classes) + \
#                   torch.pow(self.centers, 2).sum(dim=1, keepdim=True).expand(self.num_classes, batch_size).t()
#         distmat.addmm_(1, -2, x, self.centers.t())

#         classes = torch.arange(self.num_classes).long()
#         if self.use_gpu: classes = classes.cuda()
#         labels = labels.unsqueeze(1).expand(batch_size, self.num_classes)
#         mask = labels.eq(classes.expand(batch_size, self.num_classes))

#         dist = distmat * mask.float()
#         loss = dist.clamp(min=1e-12, max=1e+12).sum() / batch_size

#         return loss
    
        assert len(x) == len(labels)
        assert torch.min(labels) >= 0
        assert torch.max(labels) < self.out_features
        
        for W in self.fc.parameters():
            W = F.normalize(W, p=2, dim=1)

        x = F.normalize(x, p=2, dim=1)

        wf = self.fc(x)
#         if self.loss_type == 'cosface':
        numerator = self.s * (torch.diagonal(wf.transpose(0, 1)[labels]) - self.m)
#         if self.loss_type == 'arcface':
#             numerator = self.s * torch.cos(torch.acos(torch.clamp(torch.diagonal(wf.transpose(0, 1)[labels]), -1.+self.eps, 1-self.eps)) + self.m)
#         if self.loss_type == 'sphereface':
#             numerator = self.s * torch.cos(self.m * torch.acos(torch.clamp(torch.diagonal(wf.transpose(0, 1)[labels]), -1.+self.eps, 1-self.eps)))

        excl = torch.cat([torch.cat((wf[i, :y], wf[i, y+1:])).unsqueeze(0) for i, y in enumerate(labels)], dim=0)
        denominator = torch.exp(numerator) + torch.sum(torch.exp(self.s * excl), dim=1)
        L = numerator - torch.log(denominator)
        return -torch.mean(L)


    
# import torch
# import torch.nn as nn


class AngularPenaltySMLoss(nn.Module):

#     def __init__(self, in_features, out_features, loss_type='arcface', eps=1e-7, s=None, m=None):
#         '''
#         Angular Penalty Softmax Loss

#         Three 'loss_types' available: ['arcface', 'sphereface', 'cosface']
#         These losses are described in the following papers: 
        
#         ArcFace: https://arxiv.org/abs/1801.07698
#         SphereFace: https://arxiv.org/abs/1704.08063
#         CosFace/Ad Margin: https://arxiv.org/abs/1801.05599

#         '''
#         super(AngularPenaltySMLoss, self).__init__()
#         loss_type = loss_type.lower()
#         assert loss_type in  ['arcface', 'sphereface', 'cosface']
#         if loss_type == 'arcface':
#             self.s = 64.0 if not s else s
#             self.m = 0.5 if not m else m
#         if loss_type == 'sphereface':
#             self.s = 64.0 if not s else s
#             self.m = 1.35 if not m else m
#         if loss_type == 'cosface':
#             self.s = 30.0 if not s else s
#             self.m = 0.4 if not m else m
#         self.loss_type = loss_type
#         self.in_features = in_features
#         self.out_features = out_features
#         self.fc = nn.Linear(in_features, out_features, bias=False)
#         self.eps = eps

    def forward(self, x, labels):
        '''
        input shape (N, in_features)
        '''
        assert len(x) == len(labels)
        assert torch.min(labels) >= 0
        assert torch.max(labels) < self.out_features
        
        for W in self.fc.parameters():
            W = F.normalize(W, p=2, dim=1)

        x = F.normalize(x, p=2, dim=1)

        wf = self.fc(x)
        if self.loss_type == 'cosface':
            numerator = self.s * (torch.diagonal(wf.transpose(0, 1)[labels]) - self.m)
        if self.loss_type == 'arcface':
            numerator = self.s * torch.cos(torch.acos(torch.clamp(torch.diagonal(wf.transpose(0, 1)[labels]), -1.+self.eps, 1-self.eps)) + self.m)
        if self.loss_type == 'sphereface':
            numerator = self.s * torch.cos(self.m * torch.acos(torch.clamp(torch.diagonal(wf.transpose(0, 1)[labels]), -1.+self.eps, 1-self.eps)))

        excl = torch.cat([torch.cat((wf[i, :y], wf[i, y+1:])).unsqueeze(0) for i, y in enumerate(labels)], dim=0)
        denominator = torch.exp(numerator) + torch.sum(torch.exp(self.s * excl), dim=1)
        L = numerator - torch.log(denominator)
        return -torch.mean(L)